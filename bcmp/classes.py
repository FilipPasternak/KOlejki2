"""Reprezentacja klas klientów (zgłoszeń) w sieci BCMP.

Ten moduł ma zawierać klasy opisujące rzeczywiste obiekty „klientów” (zgłoszeń),
które poruszają się po sieci BCMP podczas symulacji lub analizy.
Na etapie metody SUM/MVA operujemy zwykle na poziomie średnich wartości,
ale można też zdefiniować strukturę do ewentualnej symulacji zdarzeń.

Zadanie dla Codex:
-------------------
- Zaimplementować klasę `CustomerClass` lub podobną, która będzie odwzorowaniem
  konfiguracji `ClassConfig` w warstwie modelu.
- Rozważyć, czy potrzebne są obiekty reprezentujące pojedynczych klientów,
  czy wystarczą liczniki na poziomie agregatów (MVA zwykle nie potrzebuje
  pojedynczych instancji klientów).
"""

from dataclasses import dataclass
from bcmp.config_schema import ClassConfig


@dataclass
class CustomerClass:
    """Reprezentacja klasy klientów w modelu.

    `CustomerClass` wiąże konfigurację (`ClassConfig`) z dynamicznym stanem,
    np. bieżącą liczbą klientów danej klasy w całej sieci (lub w węzłach).

    Zadanie dla Codex:
    -------------------
    - Dodać pola opisujące aktualny stan (jeśli potrzebne w implementacji).
    - Dodać metody pomocnicze (np. dostęp do parametrów klasy, nazwy, populacji).
    """

    config: ClassConfig
