"""Pomocnicze struktury do obsługi routingu w sieci BCMP.

Tutaj można umieścić funkcje do pracy z `RoutingEntry` i budowania
macierzy przejść między węzłami dla poszczególnych klas.
"""

from typing import Dict, List
from bcmp.config_schema import RoutingEntry


def build_routing_matrix(
    routing_entries: List[RoutingEntry],
) -> Dict[str, Dict[str, float]]:
    """Buduje słownikową „macierz” przejść z listy `RoutingEntry`.
    """
    routing_matrix: Dict[str, Dict[str, float]] = {}

    # Zbierz wszystkie węzły pojawiające się w konfiguracji
    node_ids = set()
    for entry in routing_entries:
        node_ids.add(entry.from_node_id)
        node_ids.add(entry.to_node_id)

    # Utwórz klucze dla każdego węzła (również tych bez wyjść)
    for node_id in node_ids:
        routing_matrix[node_id] = {}

    # Uzupełnij macierz i zliczaj sumę prawdopodobieństw wychodzących
    outgoing_sums: Dict[str, float] = {node_id: 0.0 for node_id in node_ids}
    for entry in routing_entries:
        from_node = entry.from_node_id
        to_node = entry.to_node_id
        probability = entry.probability

        routing_matrix[from_node][to_node] = routing_matrix[from_node].get(to_node, 0.0) + probability
        outgoing_sums[from_node] += probability

    # Walidacja: suma prawdopodobieństw wychodzących nie może przekraczać 1
    for node_id, prob_sum in outgoing_sums.items():
        if prob_sum > 1 + 1e-9:
            raise ValueError(
                f"Suma prawdopodobieństw wychodzących z węzła '{node_id}' przekracza 1: {prob_sum}"
            )

    return routing_matrix
