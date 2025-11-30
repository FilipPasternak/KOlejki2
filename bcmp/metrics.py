"""Struktury przechowujące wyniki obliczeń sieci BCMP.

Metoda SUM/MVA daje wyniki typu:
- L_i^(k) – średnia liczba klientów klasy k w węźle i,
- R_i^(k) – średni czas przebywania w węźle i dla klasy k,
- X^(k) – throughput dla klasy k,
- L_i – suma po klasach, itd.

Ten moduł ma zawierać klasy/struktury pomagające spójnie przechowywać wyniki.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class NodeClassMetrics:
    """Metryki dla jednej klasy w jednym węźle."""

    mean_customers: float = 0.0  # L_i^(k)
    mean_response_time: float = 0.0  # R_i^(k)


@dataclass
class NodeMetrics:
    """Metryki skumulowane dla pojedynczego węzła (po klasach)."""

    per_class: Dict[str, NodeClassMetrics] = field(default_factory=dict)

    @property
    def total_mean_customers(self) -> float:
        """Suma średniej liczby klientów po wszystkich klasach."""
        return sum(m.mean_customers for m in self.per_class.values())


@dataclass
class NetworkMetrics:
    """Metryki całej sieci BCMP.

    Atrybuty:
    - `per_node`: metryki per węzeł.
    - `throughput_per_class`: throughput (X^(k)) dla każdej klasy.
    - Można dodać inne pola: średni czas odpowiedzi w systemie, itp.

    Zadanie dla Codex:
    -------------------
    - Uzupełnić tę strukturę o wszystkie metryki, które będą potrzebne
      w GUI i w sprawozdaniu.
    """

    per_node: Dict[str, NodeMetrics] = field(default_factory=dict)
    throughput_per_class: Dict[str, float] = field(default_factory=dict)
