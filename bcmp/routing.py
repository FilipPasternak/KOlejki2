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

    Zadanie dla Codex:
    -------------------
    - Zaimplementować tę funkcję tak, aby zwracała strukturę:
        {from_node_id: {to_node_id: probability}}.
    - Upewnić się, że węzły bez zdefiniowanych przejść też są reprezentowane
      (np. pustym słownikiem).
    - Ewentualnie dodać walidację sum prawdopodobieństw.
    """
    # TODO: Codex – implementacja budowy macierzy routingu.
    raise NotImplementedError
