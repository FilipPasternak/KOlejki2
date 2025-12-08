"""Reprezentacja pojedynczego węzła BCMP (systemu kolejkowego).

Węzeł (service center) jest podstawowym elementem sieci BCMP. Może mieć różne typy:
- FCFS – kolejka M/M/m z obsługą w kolejności napływu,
- PS – Processor Sharing,
- IS – Infinite Server,
- LCFS_PR – Last-Come-First-Served z wywłaszczaniem.
"""

from dataclasses import dataclass, field
from typing import Dict

from bcmp.config_schema import ServiceCenterConfig


@dataclass
class ServiceCenter:
    """Pojedynczy węzeł BCMP wraz ze stanem dynamicznym.

    Atrybuty:
    - `config`: konfiguracja węzła.
    - `mean_customers_per_class`: słownik {class_id: L_i^(k)} – średnia liczba
      klientów klasy k w tym węźle (wynik MVA).
    - Można dodać inne pola (np. czasy odpowiedzi, wykorzystanie serwerów).
    """

    config: ServiceCenterConfig
    mean_customers_per_class: Dict[str, float] = field(default_factory=dict)
