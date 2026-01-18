"""Implementacja metody SUM (Summation Method) dla sieci BCMP.

Metoda SUM rozwiązuje zamknięte, wieloklasowe sieci BCMP iteracyjnie
wyznaczając przepustowości klas oraz średnie liczby klientów w węzłach.
"""

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np

from bcmp.metrics import (
    NetworkMetrics,
    NodeClassMetrics,
    NodeMetrics,
    NodePerformanceSummary,
)
from bcmp.network import BCMPNetwork


def compute_network_metrics(network: BCMPNetwork, *, eps: float = 1e-5) -> None:
    """Oblicza metryki sieci BCMP metodą SUM.

    Algorytm:
    1. Wyznaczenie współczynników wizyt dla każdej klasy na podstawie macierzy
       routingu.
    2. Iteracyjne szacowanie przepustowości klas ``lambda_r`` tak, aby
       spełniony był warunek normalizacyjny SUM: ``sum_i f_ir(lambda_r * e_ir)
       = N_r`` dla każdej klasy ``r``.
    3. Obliczenie liczby klientów ``K_i^r = f_ir(lambda_i^r)`` oraz czasów
       przebywania ``T_i^r``.
    4. Zapisanie wyników w ``network.metrics`` i aktualizacja węzłów.
    """

    node_ids = [node_config.id for node_config in network.config.nodes]
    class_ids = [cls.id for cls in network.config.classes]

    visits = _compute_visit_ratios_per_class(network, node_ids, class_ids)

    populations = [network.classes[class_id].config.population for class_id in class_ids]

    lambda_r = np.full(len(class_ids), 1e-5, dtype=float)

    max_iterations = 10_000
    relaxation = 0.3
    for _ in range(max_iterations):
        lambda_i_totals = _total_arrivals_per_node(lambda_r, visits, node_ids, class_ids)
        mean_service_times = _mean_service_time_per_node(
            network, node_ids, class_ids, lambda_r, visits
        )

        lambda_new = np.zeros_like(lambda_r)
        for class_idx, class_id in enumerate(class_ids):
            denom = 0.0
            for node_idx, node_id in enumerate(node_ids):
                arrival_ir = lambda_r[class_idx] * visits[class_id][node_idx]
                denom += _load_function(
                    network.nodes[node_id],
                    class_id,
                    arrival_ir,
                    lambda_i_totals[node_idx],
                    mean_service_times[node_idx],
                )

            lambda_new[class_idx] = (
                populations[class_idx] / denom if denom > 0 else 0.0
            )

        lambda_i_totals_new = _total_arrivals_per_node(
            lambda_new, visits, node_ids, class_ids
        )
        mean_service_times_new = _mean_service_time_per_node(
            network, node_ids, class_ids, lambda_new, visits
        )
        scale = 1.0
        for node_idx, total in enumerate(lambda_i_totals_new):
            node = network.nodes[node_ids[node_idx]]
            if node.config.node_type == "IS":
                continue
            mean_service_time = mean_service_times_new[node_idx]
            if mean_service_time <= 0:
                continue
            servers = node.config.servers or 1
            capacity = servers / mean_service_time
            if total > capacity and capacity > 0:
                scale = min(scale, (capacity / total) * 0.9)
        if scale < 1.0:
            lambda_new *= scale

        error = float(np.sum((lambda_new - lambda_r) ** 2))
        lambda_r = (1 - relaxation) * lambda_r + relaxation * lambda_new
        if error < eps:
            break
    else:
        raise RuntimeError("Metoda SUM nie zbiega się w zadanej liczbie iteracji")

    lambda_i_totals = _total_arrivals_per_node(lambda_r, visits, node_ids, class_ids)
    mean_service_times = _mean_service_time_per_node(
        network, node_ids, class_ids, lambda_r, visits
    )

    network.metrics = NetworkMetrics()
    network.metrics.visit_ratios = visits
    network.metrics.throughput_per_class = {
        class_id: float(lambda_r[class_idx]) for class_idx, class_id in enumerate(class_ids)
    }

    for node_idx, node_id in enumerate(node_ids):
        node_metrics = NodeMetrics()
        node = network.nodes[node_id]

        for class_idx, class_id in enumerate(class_ids):
            arrival_ir = lambda_r[class_idx] * visits[class_id][node_idx]
            mean_customers = _load_function(
                node,
                class_id,
                arrival_ir,
                lambda_i_totals[node_idx],
                mean_service_times[node_idx],
            )
            response_time = mean_customers / arrival_ir if arrival_ir > 0 else 0.0

            service_rate = node.config.service_rates_per_class.get(class_id, 0.0)
            service_time = 1.0 / service_rate if service_rate > 0 else 0.0
            waiting_time = max(response_time - service_time, 0.0)
            queue_length = arrival_ir * waiting_time

            servers = node.config.servers or 1
            utilization = (
                arrival_ir / (service_rate * servers)
                if service_rate > 0 and servers > 0
                else 0.0
            )

            node_metrics.per_class[class_id] = NodeClassMetrics(
                mean_customers=float(mean_customers),
                mean_response_time=response_time,
                mean_waiting_time=waiting_time,
                mean_queue_length=queue_length,
                service_time=service_time,
                arrival_rate=arrival_ir,
                utilization=utilization,
            )

        network.metrics.per_node[node_id] = node_metrics
        network.nodes[node_id].mean_customers_per_class = {
            class_id: node_metrics.per_class[class_id].mean_customers
            for class_id in class_ids
        }

    _update_node_summaries(network, node_ids)


def _load_function(
    node,
    class_id: str,
    lambda_ir: float,
    lambda_i_total: float,
    mean_service_time: float,
) -> float:
    """Zwraca wartość funkcji obciążenia f_i^r(λ_ir) zależną od typu węzła."""

    service_rate = node.config.service_rates_per_class.get(class_id)
    if service_rate is None or service_rate <= 0:
        raise ValueError(
            f"Brak poprawnej intensywności obsługi dla klasy {class_id} w węźle {node.config.id}"
        )

    node_type = node.config.node_type
    servers = node.config.servers or 1

    service_time = 1.0 / service_rate
    if node_type == "IS":
        return lambda_ir * service_time

    if node_type == "FCFS":
        mean_service_time = mean_service_time or service_time
        mu_eff = 1.0 / mean_service_time if mean_service_time > 0 else service_rate
        traffic_intensity = lambda_i_total / mu_eff if mu_eff > 0 else 0.0
        capacity_gap = servers * mu_eff - lambda_i_total
        if capacity_gap <= 0:
            capacity_gap = 1e-9
        waiting_time = _erlang_c(traffic_intensity, servers) / capacity_gap
        return lambda_ir * (service_time + waiting_time)

    if node_type in {"PS", "LCFS_PR"}:
        mean_service_time = mean_service_time or service_time
        servers = max(servers, 1)
        utilization = (lambda_i_total * mean_service_time) / servers
        if utilization >= 1:
            utilization = 1 - 1e-9
        return lambda_ir * service_time / (1 - utilization)

    # Typ 3 (M/M/∞) traktujemy tak samo jak IS zgodnie z opisem
    if node_type not in {"FCFS", "PS", "IS", "LCFS_PR"}:
        raise ValueError(f"Nieobsługiwany typ węzła: {node_type}")

    return lambda_ir / service_rate


def _mean_service_time_per_node(
    network: BCMPNetwork,
    node_ids: List[str],
    class_ids: List[str],
    lambda_r: np.ndarray,
    visits: Dict[str, np.ndarray],
) -> List[float]:
    """Wyznacza średni czas obsługi na węzłach w oparciu o miks napływów klas."""

    mean_times: List[float] = []
    for node_idx, node_id in enumerate(node_ids):
        node = network.nodes[node_id]
        total_arrival = 0.0
        weighted_time = 0.0
        for class_idx, class_id in enumerate(class_ids):
            arrival_ir = lambda_r[class_idx] * visits[class_id][node_idx]
            total_arrival += arrival_ir
            service_rate = node.config.service_rates_per_class.get(class_id)
            if service_rate is None or service_rate <= 0:
                raise ValueError(
                    f"Brak poprawnej intensywności obsługi dla klasy {class_id} w węźle {node_id}"
                )
            weighted_time += arrival_ir * (1.0 / service_rate)

        if total_arrival > 0:
            mean_times.append(weighted_time / total_arrival)
            continue

        service_times = [
            1.0 / rate
            for rate in node.config.service_rates_per_class.values()
            if rate > 0
        ]
        if service_times:
            mean_times.append(float(np.mean(service_times)))
        else:
            mean_times.append(0.0)

    return mean_times


def _erlang_c(traffic_intensity: float, servers: int) -> float:
    """Oblicza prawdopodobieństwo oczekiwania (Erlang C) dla systemu M/M/m.

    ``traffic_intensity`` odpowiada wartości ρ_i = λ_i / μ_i.
    """

    if servers <= 0:
        raise ValueError("Liczba serwerów musi być dodatnia")

    rho_per_server = traffic_intensity / servers
    if rho_per_server >= 1:
        return 1.0

    sum_terms = sum((traffic_intensity**k) / math.factorial(k) for k in range(servers))
    last_term = (traffic_intensity**servers) / (
        math.factorial(servers) * (1 - rho_per_server)
    )
    return last_term / (sum_terms + last_term)


def _total_arrivals_per_node(
    lambda_r: np.ndarray, visits: Dict[str, np.ndarray], node_ids: List[str], class_ids: List[str]
) -> List[float]:
    """Zwraca całkowitą intensywność przybyć do każdego węzła (suma po klasach)."""

    totals = [0.0 for _ in node_ids]
    for class_idx, class_id in enumerate(class_ids):
        totals = [
            totals[node_idx] + lambda_r[class_idx] * visits[class_id][node_idx]
            for node_idx in range(len(node_ids))
        ]
    return totals


def _compute_visit_ratios_per_class(
    network: BCMPNetwork, node_ids: List[str], class_ids: List[str]
) -> Dict[str, np.ndarray]:
    """Wyznacza współczynniki wizyt dla każdej klasy na podstawie macierzy routingu."""

    visits: Dict[str, np.ndarray] = {}
    for class_id in class_ids:
        routing_matrix = network.routing_matrices.get(class_id, {})
        matrix = np.zeros((len(node_ids), len(node_ids)))
        for i, from_id in enumerate(node_ids):
            outgoing = routing_matrix.get(from_id, {})
            for j, to_id in enumerate(node_ids):
                matrix[i, j] = outgoing.get(to_id, 0.0)

        visits[class_id] = _solve_visit_ratios(matrix)
    return visits


def _solve_visit_ratios(transition_matrix: np.ndarray) -> np.ndarray:
    """Rozwiązuje układ V = V * P z normalizacją V_0 = 1."""

    size = transition_matrix.shape[0]
    A = np.eye(size) - transition_matrix.T
    b = np.zeros(size)
    A[0, :] = 0.0
    A[0, 0] = 1.0
    b[0] = 1.0
    solution = np.linalg.solve(A, b)
    return solution


def _update_node_summaries(network: BCMPNetwork, node_ids: List[str]) -> None:
    """Agreguje metryki per-klasa do wskaźników kolejki dla węzłów."""

    for node_id in node_ids:
        metrics = network.metrics.per_node[node_id]

        total_arrival = 0.0
        total_waiting = 0.0
        total_system = 0.0
        total_queue_length = 0.0
        total_system_length = metrics.total_mean_customers
        total_utilization = 0.0

        for class_metrics in metrics.per_class.values():
            total_arrival += class_metrics.arrival_rate
            total_waiting += class_metrics.arrival_rate * class_metrics.mean_waiting_time
            total_system += class_metrics.arrival_rate * class_metrics.mean_response_time
            total_queue_length += class_metrics.mean_queue_length
            total_utilization += class_metrics.utilization

        mean_waiting = total_waiting / total_arrival if total_arrival > 0 else 0.0
        mean_system = total_system / total_arrival if total_arrival > 0 else 0.0

        metrics.summary = NodePerformanceSummary(
            mean_queue_length=total_queue_length,
            mean_system_length=total_system_length,
            mean_waiting_time=mean_waiting,
            mean_system_time=mean_system,
            utilization=total_utilization,
        )
