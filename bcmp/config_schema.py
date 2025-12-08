"""Struktury konfiguracyjne opisujące sieć BCMP.

Ten moduł ma zawierać *czyste dane* opisujące model:
- listę węzłów (5+ węzłów kolejkowych),
- listę klas klientów (4+ klasy zgłoszeń),
- macierze routingu dla każdej klasy,
- informacje o liczbie klientów w każdej klasie (zamknięta sieć),
- parametry obsługi w węzłach.
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional


NodeType = Literal["FCFS", "PS", "IS", "LCFS_PR"]


@dataclass
class ServiceCenterConfig:
    """Opis pojedynczego węzła (systemu kolejkowego) w sieci BCMP.

    Atrybuty:
    - `id`: unikalny identyfikator węzła (np. liczba całkowita lub string).
    - `name`: czytelna nazwa (np. "Rejestracja", "I linia" itp.).
    - `node_type`: typ węzła zgodny z klasą BCMP (FCFS, PS, IS, LCFS_PR).
    - `servers`: liczba serwerów (dla IS można traktować jako None lub bardzo dużą liczbę).
    - `service_rates_per_class`: słownik {class_id: mu_i^(k)} – intensywności obsługi
      dla danej klasy w tym węźle.

    Można dodać inne parametry (np. priorytety), jeśli zajdzie potrzeba.
    """

    id: str
    name: str
    node_type: NodeType
    servers: Optional[int]
    service_rates_per_class: Dict[str, float]


@dataclass
class ClassConfig:
    """Opis pojedynczej klasy zgłoszeń (klienta) w sieci BCMP.

    Atrybuty:
    - `id`: unikalny identyfikator klasy (np. "P1", "P2", "P3", "P4").
    - `name`: czytelna nazwa klasy (np. "Awaria krytyczna").
    - `population`: liczba klientów tej klasy w systemie (sieć zamknięta).
    - `priority`: opcjonalna informacja o priorytecie (do wykorzystania w analizie).

    UWAGA: klasa klienta jest **stała** – klient nie zmienia przynależności do klasy
    podczas przejścia przez sieć.
    """

    id: str
    name: str
    population: int
    priority: Optional[int] = None


@dataclass
class RoutingEntry:
    """Pojedynczy wpis w schemacie routingu dla danej klasy.

    Atrybuty:
    - `from_node_id`: identyfikator węzła źródłowego.
    - `to_node_id`: identyfikator węzła docelowego lub specjalna wartość (np. "OUT")
      oznaczająca wyjście z systemu.
    - `probability`: prawdopodobieństwo przejścia.
    """

    from_node_id: str
    to_node_id: str
    probability: float


@dataclass
class NetworkConfig:
    """Główna konfiguracja sieci BCMP.

    Atrybuty:
    - `nodes`: lista konfiguracji węzłów (min. 5 o różnych typach).
    - `classes`: lista konfiguracji klas (min. 4).
    - `routing_per_class`: słownik {class_id: lista RoutingEntry} opisujący
      macierze przejść osobno dla każdej klasy.
    - `description`: krótki opis systemu (np. "System obsługi zgłoszeń helpdesk").
    """

    nodes: List[ServiceCenterConfig]
    classes: List[ClassConfig]
    routing_per_class: Dict[str, List[RoutingEntry]]
    description: str = ""
