"""Implementacja metody SUM / Mean Value Analysis (MVA) dla sieci BCMP.

Ten moduł ma zawierać algorytmy obliczające średnie wartości w sieci BCMP
(zamkniętej, wieloklasowej).

Docelowo:
- Funkcja główna, np. `compute_network_metrics(network: BCMPNetwork) -> None`,
  która:
    * pobiera parametry sieci z `network.config` oraz z węzłów,
    * wykonuje iteracyjny algorytm MVA (metoda SUM),
    * zapisuje wyniki w `network.metrics` oraz w polach węzłów.

- Ewentualne funkcje pomocnicze do obsługi poszczególnych typów węzłów BCMP:
  (FCFS, PS, IS, LCFS_PR).

Zadanie dla Codex:
-------------------
- Zaimplementować kompletny algorytm MVA dla przygotowanego modelu sieci.
- Zadbać o:
    * czytelność i komentowanie kodu (to projekt na studia),
    * walidację danych wejściowych,
    * ewentualną możliwość późniejszej rozbudowy (np. inne typy węzłów).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

from bcmp.metrics import NetworkMetrics, NodeClassMetrics, NodeMetrics
from bcmp.network import BCMPNetwork


def compute_network_metrics(network: BCMPNetwork) -> None:
    """Oblicza metryki sieci BCMP metodą SUM/MVA i zapisuje je w `network`.

    Implementacja zakłada zamkniętą, wieloklasową sieć BCMP i wykorzystuje
    klasyczny algorytm Mean Value Analysis. W obliczeniach używamy wizyt
    (visit ratios) wyznaczonych z macierzy routingu dla każdej klasy, a
    następnie iteracyjnie zwiększamy populację klientów do zadanej wartości.
    """

    node_ids = [node_config.id for node_config in network.config.nodes]
    class_ids = [cls.id for cls in network.config.classes]

    visits = _compute_visit_ratios_per_class(network, node_ids, class_ids)

    populations = [network.classes[class_id].config.population for class_id in class_ids]
    total_population = sum(populations)

    state_metrics: Dict[Tuple[int, ...], np.ndarray] = {
        tuple(0 for _ in class_ids): np.zeros((len(node_ids), len(class_ids)))
    }
    throughput_per_class: Dict[str, float] = {class_id: 0.0 for class_id in class_ids}

    for total_clients in range(1, total_population + 1):
        for state in _generate_states_for_total(total_clients, populations):
            L_state = np.zeros((len(node_ids), len(class_ids)))
            for class_idx, class_id in enumerate(class_ids):
                if state[class_idx] == 0:
                    continue

                prev_state = list(state)
                prev_state[class_idx] -= 1
                prev_key = tuple(prev_state)
                prev_L = state_metrics[prev_key]

                total_L_prev = prev_L.sum(axis=1)
                R = np.array(
                    [
                        _mean_response_time(
                            network.nodes[node_id], class_id, total_L_prev[node_idx]
                        )
                        for node_idx, node_id in enumerate(node_ids)
                    ]
                )

                denom = float(np.sum(visits[class_id] * R))
                X_k = state[class_idx] / denom if denom > 0 else 0.0
                throughput_per_class[class_id] = X_k

                for node_idx, node_id in enumerate(node_ids):
                    L_state[node_idx, class_idx] = X_k * visits[class_id][node_idx] * R[node_idx]

            state_metrics[state] = L_state

    final_state = tuple(populations)
    final_L = state_metrics[final_state]

    network.metrics = NetworkMetrics()
    network.metrics.throughput_per_class = throughput_per_class

    for node_idx, node_id in enumerate(node_ids):
        node_metrics = NodeMetrics()

        for class_idx, class_id in enumerate(class_ids):
            mean_customers = float(final_L[node_idx, class_idx])
            prev_state = list(final_state)
            prev_state[class_idx] -= 1 if prev_state[class_idx] > 0 else 0
            prev_L = state_metrics.get(tuple(prev_state), np.zeros_like(final_L))
            R = _mean_response_time(
                network.nodes[node_id], class_id, prev_L.sum(axis=1)[node_idx]
            )
            node_metrics.per_class[class_id] = NodeClassMetrics(
                mean_customers=mean_customers,
                mean_response_time=float(R),
            )

        network.metrics.per_node[node_id] = node_metrics
        network.nodes[node_id].mean_customers_per_class = {
            class_id: float(final_L[node_idx, class_idx]) for class_idx, class_id in enumerate(class_ids)
        }


def _generate_states_for_total(total: int, limits: Sequence[int]) -> Iterable[Tuple[int, ...]]:
    """Generuje wszystkie wektory populacji o zadanej sumie i ograniczeniach."""

    def _helper(idx: int, remaining: int, current: List[int]) -> Iterable[Tuple[int, ...]]:
        if idx == len(limits) - 1:
            if remaining <= limits[idx]:
                yield tuple(current + [remaining])
            return

        max_here = min(remaining, limits[idx])
        for value in range(max_here + 1):
            yield from _helper(idx + 1, remaining - value, current + [value])

    return list(_helper(0, total, []))


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


def _mean_response_time(node, class_id: str, mean_customers_total: float) -> float:
    """Zwraca średni czas przebywania w węźle dla danej klasy."""

    service_rate = node.config.service_rates_per_class.get(class_id)
    if service_rate is None or service_rate <= 0:
        raise ValueError(f"Brak poprawnej intensywności obsługi dla klasy {class_id} w węźle {node.config.id}")

    service_time = 1.0 / service_rate

    if node.config.node_type == "IS":
        return service_time

    servers = node.config.servers or 1
    if node.config.node_type in {"FCFS", "PS", "LCFS_PR"}:
        return service_time * (1.0 + mean_customers_total / servers)

    raise ValueError(f"Nieobsługiwany typ węzła: {node.config.node_type}")
