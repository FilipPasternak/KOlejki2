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

from typing import Optional

from bcmp.config_schema import NetworkConfig
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
    raise NotImplementedError


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
