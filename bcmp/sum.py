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


def compute_network_metrics(network: BCMPNetwork, *, eps: float = 1e-6) -> None:
    node_ids = [node_config.id for node_config in network.config.nodes]
    class_ids = [cls.id for cls in network.config.classes]

    _validate_routing(network, node_ids, class_ids)

    visits = _compute_visit_ratios_per_class(network, node_ids, class_ids)
    _validate_visits(visits)

    populations = [network.classes[class_id].config.population for class_id in class_ids]

    lambda_r = np.array([max(1e-6, float(pop) / 10.0) for pop in populations], dtype=float)

    max_iterations = 50_000
    relaxation = 0.1
    prev_error = float("inf")

    for _ in range(max_iterations):
        lambda_i_totals = _total_arrivals_per_node(lambda_r, visits, node_ids, class_ids)
        mean_service_times = _mean_service_time_per_node(
            network, node_ids, class_ids, lambda_r, visits
        )

        lambda_new = np.zeros_like(lambda_r)

        for class_idx, class_id in enumerate(class_ids):
            denom = 0.0
            for node_idx, node_id in enumerate(node_ids):
                arrival_ir = float(lambda_r[class_idx] * visits[class_id][node_idx])
                denom += _load_function(
                    network.nodes[node_id],
                    class_id,
                    arrival_ir,
                    float(lambda_i_totals[node_idx]),
                    float(mean_service_times[node_idx]),
                )

            if denom > 0.0:
                # FIX: domykanie populacji, bo denom = Σ_i K_i^r(λ_r)
                lambda_new[class_idx] = float(lambda_r[class_idx]) * (
                    float(populations[class_idx]) / denom
                )
            else:
                lambda_new[class_idx] = 0.0

        diff = float(np.max(np.abs(lambda_new - lambda_r)))
        scale = float(np.max(np.abs(lambda_r))) + 1e-12
        error = diff / scale

        if error > prev_error * 1.05:
            relaxation = max(0.02, relaxation * 0.7)
        prev_error = error

        lambda_r = (1.0 - relaxation) * lambda_r + relaxation * lambda_new

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
        node_type = node.config.node_type
        servers = node.config.servers or 1

        for class_idx, class_id in enumerate(class_ids):
            arrival_ir = float(lambda_r[class_idx] * visits[class_id][node_idx])

            mean_customers = float(
                _load_function(
                    node,
                    class_id,
                    arrival_ir,
                    float(lambda_i_totals[node_idx]),
                    float(mean_service_times[node_idx]),
                )
            )

            service_rate = float(node.config.service_rates_per_class.get(class_id, 0.0))
            service_time = 1.0 / service_rate if service_rate > 0 else 0.0

            if arrival_ir > 0:
                if node_type == "FCFS":
                    in_service = arrival_ir / service_rate if service_rate > 0 else 0.0
                    queue_length = max(mean_customers - in_service, 0.0)
                    waiting_time = queue_length / arrival_ir
                    response_time = waiting_time + service_time
                else:
                    response_time = mean_customers / arrival_ir
                    waiting_time = max(response_time - service_time, 0.0)
                    queue_length = arrival_ir * waiting_time
            else:
                response_time = 0.0
                waiting_time = 0.0
                queue_length = 0.0

            utilization = (
                arrival_ir / (service_rate * servers)
                if service_rate > 0 and servers > 0
                else 0.0
            )

            node_metrics.per_class[class_id] = NodeClassMetrics(
                mean_customers=float(mean_customers),
                mean_response_time=float(response_time),
                mean_waiting_time=float(waiting_time),
                mean_queue_length=float(queue_length),
                service_time=float(service_time),
                arrival_rate=float(arrival_ir),
                utilization=float(utilization),
            )

        network.metrics.per_node[node_id] = node_metrics
        network.nodes[node_id].mean_customers_per_class = {
            class_id: node_metrics.per_class[class_id].mean_customers
            for class_id in class_ids
        }

    _update_node_summaries(network, node_ids)


def _validate_routing(network: BCMPNetwork, node_ids: List[str], class_ids: List[str]) -> None:
    for class_id in class_ids:
        rm = network.routing_matrices.get(class_id, {})
        for from_id in node_ids:
            outgoing = rm.get(from_id, {})
            s = 0.0
            for to_id in node_ids:
                s += float(outgoing.get(to_id, 0.0))
            if s > 0.0 and abs(s - 1.0) > 1e-6:
                raise RuntimeError(
                    f"Routing nie sumuje się do 1: klasa={class_id}, from={from_id}, sum={s}"
                )


def _validate_visits(visits: Dict[str, np.ndarray]) -> None:
    for class_id, v in visits.items():
        if not np.all(np.isfinite(v)):
            raise RuntimeError(f"Visit ratios mają NaN/inf dla klasy {class_id}: {v}")
        if np.any(v < 0):
            raise RuntimeError(f"Visit ratios ujemne dla klasy {class_id}: {v}")
        if float(np.sum(v)) == 0.0:
            raise RuntimeError(f"Visit ratios sumują się do 0 dla klasy {class_id}: {v}")


def _load_function(
    node,
    class_id: str,
    lambda_ir: float,
    lambda_i_total: float,
    mean_service_time: float,
) -> float:
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
        m = max(int(servers), 1)
        if mean_service_time <= 0:
            mean_service_time = service_time

        a = lambda_i_total * mean_service_time
        rho_i = a / m
        if rho_i >= 1.0:
            return 1e12

        P_wait = _erlang_c(a, m)

        rho_ir = lambda_ir / (service_rate * m)
        in_service = lambda_ir / service_rate

        queue_part = rho_ir * (P_wait / (1.0 - rho_i))
        return in_service + queue_part

    if node_type in {"PS", "LCFS_PR"}:
        if mean_service_time <= 0:
            mean_service_time = service_time

        m = max(int(servers), 1)
        utilization = (lambda_i_total * mean_service_time) / m
        if utilization >= 1.0:
            utilization = 1.0 - 1e-9

        return lambda_ir * service_time / (1.0 - utilization)

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
    mean_times: List[float] = []

    for node_idx, node_id in enumerate(node_ids):
        node = network.nodes[node_id]
        total_arrival = 0.0
        weighted_time = 0.0

        for class_idx, class_id in enumerate(class_ids):
            arrival_ir = float(lambda_r[class_idx] * visits[class_id][node_idx])
            total_arrival += arrival_ir

            service_rate = node.config.service_rates_per_class.get(class_id)
            if service_rate is None or service_rate <= 0:
                raise ValueError(
                    f"Brak poprawnej intensywności obsługi dla klasy {class_id} w węźle {node_id}"
                )
            weighted_time += arrival_ir * (1.0 / float(service_rate))

        if total_arrival > 0.0:
            mean_times.append(weighted_time / total_arrival)
            continue

        service_times = [
            1.0 / float(rate)
            for rate in node.config.service_rates_per_class.values()
            if rate and rate > 0
        ]
        mean_times.append(float(np.mean(service_times)) if service_times else 0.0)

    return mean_times


def _erlang_c(a_offered: float, servers: int) -> float:
    if servers <= 0:
        raise ValueError("Liczba serwerów musi być dodatnia")
    if a_offered <= 0.0:
        return 0.0

    rho = a_offered / servers
    if rho >= 1.0:
        return 1.0

    sum_terms = sum((a_offered**k) / math.factorial(k) for k in range(servers))
    last_term = (a_offered**servers) / (math.factorial(servers) * (1.0 - rho))
    return last_term / (sum_terms + last_term)


def _total_arrivals_per_node(
    lambda_r: np.ndarray,
    visits: Dict[str, np.ndarray],
    node_ids: List[str],
    class_ids: List[str],
) -> List[float]:
    totals = [0.0 for _ in node_ids]
    for class_idx, class_id in enumerate(class_ids):
        totals = [
            totals[node_idx] + float(lambda_r[class_idx] * visits[class_id][node_idx])
            for node_idx in range(len(node_ids))
        ]
    return totals


def _compute_visit_ratios_per_class(
    network: BCMPNetwork, node_ids: List[str], class_ids: List[str]
) -> Dict[str, np.ndarray]:
    visits: Dict[str, np.ndarray] = {}

    for class_id in class_ids:
        routing_matrix = network.routing_matrices.get(class_id, {})
        matrix = np.zeros((len(node_ids), len(node_ids)))

        for i, from_id in enumerate(node_ids):
            outgoing = routing_matrix.get(from_id, {})
            for j, to_id in enumerate(node_ids):
                matrix[i, j] = float(outgoing.get(to_id, 0.0))

        visits[class_id] = _solve_visit_ratios(matrix)

    return visits


def _solve_visit_ratios(transition_matrix: np.ndarray) -> np.ndarray:
    size = transition_matrix.shape[0]
    A = np.eye(size) - transition_matrix.T
    b = np.zeros(size)

    A[0, :] = 0.0
    A[0, 0] = 1.0
    b[0] = 1.0

    solution = np.linalg.solve(A, b)
    return solution


def _update_node_summaries(network: BCMPNetwork, node_ids: List[str]) -> None:
    for node_id in node_ids:
        metrics = network.metrics.per_node[node_id]

        total_arrival = 0.0
        total_waiting = 0.0
        total_system = 0.0
        total_queue_length = 0.0
        total_system_length = metrics.total_mean_customers
        total_utilization = 0.0

        for class_metrics in metrics.per_class.values():
            total_arrival += float(class_metrics.arrival_rate)
            total_waiting += float(class_metrics.arrival_rate * class_metrics.mean_waiting_time)
            total_system += float(class_metrics.arrival_rate * class_metrics.mean_response_time)
            total_queue_length += float(class_metrics.mean_queue_length)
            total_utilization += float(class_metrics.utilization)

        mean_waiting = total_waiting / total_arrival if total_arrival > 0 else 0.0
        mean_system = total_system / total_arrival if total_arrival > 0 else 0.0

        metrics.summary = NodePerformanceSummary(
            mean_queue_length=float(total_queue_length),
            mean_system_length=float(total_system_length),
            mean_waiting_time=float(mean_waiting),
            mean_system_time=float(mean_system),
            utilization=float(total_utilization),
        )
