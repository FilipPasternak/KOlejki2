"""Główna klasa reprezentująca sieć BCMP.

`BCMPNetwork` łączy:
- konfigurację (`NetworkConfig`),
- kolekcję węzłów (`ServiceCenter`),
- kolekcję klas (`CustomerClass`),
- pomocnicze struktury routingu,
- aktualne metryki (`NetworkMetrics`).

W niej umieszczamy logikę niezależną od GUI oraz od szczegółów implementacji MVA.
"""

from dataclasses import dataclass, field
from typing import Dict

from bcmp.config_schema import NetworkConfig
from bcmp.classes import CustomerClass
from bcmp.metrics import NetworkMetrics
from bcmp.node import ServiceCenter
from bcmp import routing


@dataclass
class BCMPNetwork:
    """Model sieci BCMP dla systemu obsługi zgłoszeń.

    Zadania tej klasy:
    ------------------
    - Przechowywać konfigurację sieci (`NetworkConfig`).
    - Na jej podstawie tworzyć:
        * obiekty `ServiceCenter` dla każdego węzła,
        * obiekty `CustomerClass` dla każdej klasy.
    - Budować struktury routingu (np. słowniki macierzy przejść z modułu `routing`).
    - Przechowywać wyniki obliczeń MVA w obiekcie `NetworkMetrics`.
    """

    config: NetworkConfig
    nodes: Dict[str, ServiceCenter] = field(default_factory=dict)
    classes: Dict[str, CustomerClass] = field(default_factory=dict)
    routing_matrices: Dict[str, Dict[str, Dict[str, float]]] = field(default_factory=dict)
    metrics: NetworkMetrics = field(default_factory=NetworkMetrics)

    def __post_init__(self) -> None:
        """Tworzy obiekty węzłów, klas i struktur routingu na podstawie konfiguracji.
        """
        self.nodes = {
            node_config.id: ServiceCenter(node_config)
            for node_config in self.config.nodes
        }

        self.classes = {
            class_config.id: CustomerClass(class_config)
            for class_config in self.config.classes
        }

        self.routing_matrices = {
            class_id: routing.build_routing_matrix(entries)
            for class_id, entries in self.config.routing_per_class.items()
        }
