"""Reprezentacja klas klientów (zgłoszeń) w sieci BCMP.

Ten moduł ma zawierać klasy opisujące rzeczywiste obiekty „klientów” (zgłoszeń),
które poruszają się po sieci BCMP podczas symulacji lub analizy.
Na etapie metody SUM/MVA operujemy zwykle na poziomie średnich wartości,
ale można też zdefiniować strukturę do ewentualnej symulacji zdarzeń.
"""

from dataclasses import dataclass
from bcmp.config_schema import ClassConfig


@dataclass
class CustomerClass:
    """Reprezentacja klasy klientów w modelu.

    `CustomerClass` wiąże konfigurację (`ClassConfig`) z dynamicznym stanem,
    np. bieżącą liczbą klientów danej klasy w całej sieci (lub w węzłach).
    """

    config: ClassConfig
