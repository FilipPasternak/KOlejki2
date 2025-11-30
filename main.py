"""Główny punkt wejścia aplikacji sieci kolejkowej BCMP.

Ten plik ma zostać uzupełniony przez Codex tak, aby:
1. Wczytywać/definiować konfigurację sieci BCMP (5+ węzłów, 4+ klasy zgłoszeń).
2. Tworzyć obiekt sieci BCMP (klasa `BCMPNetwork` z modułu `bcmp.network`).
3. Uruchamiać obliczenia metodą SUM / MVA (funkcje z `bcmp.mva_sum`).
4. Uruchomić GUI (moduł `gui.app`) i przekazać do niego referencję do modelu/warstwy logiki.
5. Umożliwiać użytkownikowi:
   - przegląd konfiguracji sieci (węzły, klasy, routing),
   - modyfikację podstawowych parametrów (np. liczba klientów w klasach, czasy obsługi),
   - wywołanie ponownego przeliczenia sieci,
   - podgląd wyników (średnie liczby klientów, czasy, throughput) w oknach GUI.

W projekcie zakładamy:
- sieć **zamkniętą** (łączna liczba klientów każdej klasy jest stała),
- **brak zmiany klasy** w trakcie przejścia przez sieć,
- co najmniej 5 węzłów różnego typu (FCFS, PS, IS, ewentualnie LCFS-PR),
- co najmniej 4 klasy zgłoszeń (np. różne priorytety / typy ticketów).
"""

from bcmp.config_schema import ClassConfig, NetworkConfig, RoutingEntry, ServiceCenterConfig
from bcmp.network import BCMPNetwork
from bcmp import mva_sum
from gui.app import run_gui


def load_default_config() -> NetworkConfig:
    """Zwraca domyślną konfigurację sieci BCMP dla systemu obsługi zgłoszeń.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować stworzenie obiektu `NetworkConfig`, który opisuje
      kompletną sieć BCMP do projektu:
        * min. 5 węzłów (różne typy: FCFS, PS, IS, ewentualnie LCFS-PR),
        * min. 4 klasy zgłoszeń,
        * zamknięta sieć (stała liczba klientów per klasa),
        * pełne macierze routingu dla każdej klasy.
    - Warto użyć czytelnych nazw (np. "Rejestracja", "I linia", "II linia" itd.).
    - Można później dodać wczytywanie konfiguracji z pliku (JSON/YAML),
      ale na początek wystarczy „zaszyta” konfiguracja w kodzie.
    """
    # TODO: Codex – zaimplementuj utworzenie NetworkConfig z przykładowymi danymi.
    classes = [
        ClassConfig(id="VIP", name="VIP / Krytyczne", population=3, priority=1),
        ClassConfig(id="STD", name="Standard", population=8, priority=2),
        ClassConfig(id="BATCH", name="Zadania wsadowe", population=5, priority=3),
        ClassConfig(id="MAINT", name="Konserwacja", population=2, priority=4),
    ]

    nodes = [
        ServiceCenterConfig(
            id="INTAKE",
            name="Rejestracja zgłoszenia",
            node_type="FCFS",
            servers=2,
            service_rates_per_class={
                "VIP": 4.5,
                "STD": 3.5,
                "BATCH": 2.5,
                "MAINT": 2.0,
            },
        ),
        ServiceCenterConfig(
            id="PRE_DIAG",
            name="Szybka diagnostyka",
            node_type="PS",
            servers=3,
            service_rates_per_class={
                "VIP": 6.0,
                "STD": 4.0,
                "BATCH": 3.0,
                "MAINT": 2.5,
            },
        ),
        ServiceCenterConfig(
            id="OPS",
            name="Obsługa operacyjna",
            node_type="FCFS",
            servers=4,
            service_rates_per_class={
                "VIP": 5.0,
                "STD": 3.8,
                "BATCH": 2.8,
                "MAINT": 2.2,
            },
        ),
        ServiceCenterConfig(
            id="LAB",
            name="Analizy / IS",
            node_type="IS",
            servers=None,
            service_rates_per_class={
                "VIP": 7.5,
                "STD": 6.0,
                "BATCH": 5.5,
                "MAINT": 4.5,
            },
        ),
        ServiceCenterConfig(
            id="ESC",
            name="Eskalacja krytyczna",
            node_type="LCFS_PR",
            servers=1,
            service_rates_per_class={
                "VIP": 5.5,
                "STD": 4.0,
                "BATCH": 3.0,
                "MAINT": 2.8,
            },
        ),
    ]

    routing_per_class = {
        "VIP": [
            RoutingEntry("INTAKE", "PRE_DIAG", 0.6),
            RoutingEntry("INTAKE", "OPS", 0.4),
            RoutingEntry("PRE_DIAG", "OPS", 0.4),
            RoutingEntry("PRE_DIAG", "LAB", 0.35),
            RoutingEntry("PRE_DIAG", "INTAKE", 0.25),
            RoutingEntry("OPS", "LAB", 0.35),
            RoutingEntry("OPS", "ESC", 0.15),
            RoutingEntry("OPS", "INTAKE", 0.5),
            RoutingEntry("LAB", "OPS", 0.5),
            RoutingEntry("LAB", "INTAKE", 0.5),
            RoutingEntry("ESC", "LAB", 0.45),
            RoutingEntry("ESC", "INTAKE", 0.55),
        ],
        "STD": [
            RoutingEntry("INTAKE", "PRE_DIAG", 0.5),
            RoutingEntry("INTAKE", "OPS", 0.5),
            RoutingEntry("PRE_DIAG", "OPS", 0.5),
            RoutingEntry("PRE_DIAG", "LAB", 0.2),
            RoutingEntry("PRE_DIAG", "INTAKE", 0.3),
            RoutingEntry("OPS", "LAB", 0.25),
            RoutingEntry("OPS", "INTAKE", 0.75),
            RoutingEntry("LAB", "OPS", 0.6),
            RoutingEntry("LAB", "INTAKE", 0.4),
            RoutingEntry("ESC", "INTAKE", 1.0),
        ],
        "BATCH": [
            RoutingEntry("INTAKE", "OPS", 0.7),
            RoutingEntry("INTAKE", "LAB", 0.3),
            RoutingEntry("OPS", "LAB", 0.5),
            RoutingEntry("OPS", "INTAKE", 0.5),
            RoutingEntry("LAB", "OPS", 0.65),
            RoutingEntry("LAB", "INTAKE", 0.35),
            RoutingEntry("PRE_DIAG", "OPS", 0.6),
            RoutingEntry("PRE_DIAG", "INTAKE", 0.4),
            RoutingEntry("ESC", "OPS", 0.5),
            RoutingEntry("ESC", "INTAKE", 0.5),
        ],
        "MAINT": [
            RoutingEntry("INTAKE", "OPS", 0.4),
            RoutingEntry("INTAKE", "PRE_DIAG", 0.3),
            RoutingEntry("INTAKE", "LAB", 0.3),
            RoutingEntry("PRE_DIAG", "LAB", 0.45),
            RoutingEntry("PRE_DIAG", "INTAKE", 0.55),
            RoutingEntry("OPS", "LAB", 0.2),
            RoutingEntry("OPS", "ESC", 0.2),
            RoutingEntry("OPS", "INTAKE", 0.6),
            RoutingEntry("LAB", "INTAKE", 0.5),
            RoutingEntry("LAB", "OPS", 0.5),
            RoutingEntry("ESC", "LAB", 0.4),
            RoutingEntry("ESC", "INTAKE", 0.6),
        ],
    }

    return NetworkConfig(
        nodes=nodes,
        classes=classes,
        routing_per_class=routing_per_class,
        description=(
            "Domyślna sieć BCMP opisująca obieg zgłoszeń od rejestracji po eskalację"
            " z rozróżnieniem klas klientów."
        ),
    )


def build_network(config: NetworkConfig) -> BCMPNetwork:
    """Buduje obiekt `BCMPNetwork` na podstawie konfiguracji.

    Zadanie dla Codex:
    -------------------
    - Wywołać konstruktor BCMPNetwork, przekazując obiekt konfiguracji.
    - Ewentualnie wykonać walidację konfiguracji (np. sprawdzić czy sumy
      prawdopodobieństw routingu <= 1, czy typy węzłów są obsługiwane).
    """
    return BCMPNetwork(config=config)


def precompute_initial_metrics(network: BCMPNetwork) -> None:
    """Przeprowadza podstawowe obliczenia sieci (metoda SUM/MVA) przed startem GUI.

    Zadanie dla Codex:
    -------------------
    - Wywołać odpowiednie funkcje z `bcmp.mva_sum`:
        * np. `mva_sum.compute_network_metrics(network)`,
      które:
        * na podstawie parametrów węzłów i klas, liczby klientów,
        * iteracyjnie obliczą średnią liczbę klientów w węzłach,
          czasy odpowiedzi, throughput itd.
    - Wyniki zapisać wewnątrz obiektu `network` (np. w atrybucie `metrics`)
      lub w dedykowanej strukturze `NetworkMetrics`.
    """
    # TODO: Codex – obliczenia metodą SUM i zapis wyników w modelu.
    mva_sum.compute_network_metrics(network)


def main() -> None:
    """Funkcja główna uruchamiająca aplikację.

    Przewidywany przebieg:
    1. Załaduj domyślną konfigurację sieci BCMP (5+ węzłów, 4+ klasy).
    2. Zbuduj obiekt sieci (`BCMPNetwork`).
    3. Wstępnie przelicz metryki metodą SUM/MVA.
    4. Uruchom GUI, przekazując obiekt `network` (i ewentualnie obiekt wyników).
    5. GUI powinno umożliwić zmianę części parametrów i ponowne przeliczenie.

    Uwaga:
    - Funkcja `run_gui` powinna uruchomić główną pętlę zdarzeń frameworka GUI
      (np. PyQt6) i zapewnić komunikację (sygnały/sloty lub callbacki)
      między interfejsem a modelem BCMP.
    """
    config = load_default_config()
    network = build_network(config)
    precompute_initial_metrics(network)
    run_gui(network)


if __name__ == "__main__":
    main()
