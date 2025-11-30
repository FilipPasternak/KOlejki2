"""Reprezentacja pojedynczego węzła BCMP (systemu kolejkowego).

Węzeł (service center) jest podstawowym elementem sieci BCMP. Może mieć różne typy:
- FCFS – kolejka M/M/m z obsługą w kolejności napływu,
- PS – Processor Sharing,
- IS – Infinite Server,
- LCFS_PR – Last-Come-First-Served z wywłaszczaniem.

Zadanie dla Codex:
-------------------
- Zaimplementować klasę `ServiceCenter`, która:
    * przechowuje konfigurację węzła (`ServiceCenterConfig`),
    * przechowuje aktualny stan (np. średnie liczby klientów per klasa,
      obliczone w MVA),
    * dostarcza metody pomocnicze używane przez algorytm SUM/MVA.

- W zależności od potrzeb projektu można tutaj zaimplementować również
  funkcje pomocnicze specyficzne dla typów węzłów (np. wzory na średnie
  czasy odpowiedzi dla danego typu przy zadanych parametrach).
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

    Zadanie dla Codex:
    -------------------
    - Uzupełnić tę klasę o metody używane przez algorytm MVA:
        * obliczanie średniego czasu przebywania w węźle dla danej klasy,
        * aktualizację `mean_customers_per_class` w kolejnych iteracjach MVA.
    """

    config: ServiceCenterConfig
    mean_customers_per_class: Dict[str, float] = field(default_factory=dict)
