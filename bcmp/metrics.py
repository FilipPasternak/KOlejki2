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
    mean_waiting_time: float = 0.0  # Wq_i^(k)
    mean_queue_length: float = 0.0  # Lq_i^(k)
    service_time: float = 0.0
    arrival_rate: float = 0.0
    utilization: float = 0.0


@dataclass
class NodeMetrics:
    """Metryki skumulowane dla pojedynczego węzła (po klasach)."""

    per_class: Dict[str, NodeClassMetrics] = field(default_factory=dict)
    summary: "NodePerformanceSummary" or None = None
    empirical_summary: "NodePerformanceSummary" or None = None

    @property
    def total_mean_customers(self) -> float:
        """Suma średniej liczby klientów po wszystkich klasach."""
        return sum(m.mean_customers for m in self.per_class.values())


@dataclass
class NodePerformanceSummary:
    """Zbiorczy zestaw metryk kolejki (analitycznych lub empirycznych)."""

    mean_queue_length: float = 0.0  # Lq
    mean_system_length: float = 0.0  # L
    mean_waiting_time: float = 0.0  # Wq
    mean_system_time: float = 0.0  # W
    utilization: float = 0.0  # ρ


@dataclass
class NetworkMetrics:
    """Metryki całej sieci BCMP.

    Atrybuty:
    - `per_node`: metryki per węzeł.
    - `throughput_per_class`: throughput (X^(k)) dla każdej klasy.
    - Można dodać inne pola: średni czas odpowiedzi w systemie, itp.
    """

    per_node: Dict[str, NodeMetrics] = field(default_factory=dict)
    throughput_per_class: Dict[str, float] = field(default_factory=dict)
    visit_ratios: Dict[str, object] = field(default_factory=dict)
