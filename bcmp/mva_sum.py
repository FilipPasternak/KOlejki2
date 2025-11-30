"""Implementacja metody SUM / Mean Value Analysis (MVA) dla sieci BCMP.

Ten moduł ma zawierać algorytmy obliczające średnie wartości w sieci BCMP
(zamkniętej, wieloklasowej).

Docelowo:
- Funkcja główna, np. `compute_network_metrics(network: BCMPNetwork) -> None`,
  która:
    * pobiera parametry sieci z `network.config` oraz z węzłów,
    * wykonuje iteracyjny algorytm MVA (metoda SUM),
    * zapisuje wyniki w `network.metrics` oraz w polach węzłów.

- Ewentualne funkcje pomocnicze do obsługi poszczególnych typów węzłów BCMP:
  (FCFS, PS, IS, LCFS_PR).

Zadanie dla Codex:
-------------------
- Zaimplementować kompletny algorytm MVA dla przygotowanego modelu sieci.
- Zadbać o:
    * czytelność i komentowanie kodu (to projekt na studia),
    * walidację danych wejściowych,
    * ewentualną możliwość późniejszej rozbudowy (np. inne typy węzłów).
"""

from bcmp.network import BCMPNetwork


def compute_network_metrics(network: BCMPNetwork) -> None:
    """Oblicza metryki sieci BCMP metodą SUM/MVA i zapisuje je w `network`.

    Parametry:
    ----------
    network : BCMPNetwork
        Obiekt sieci BCMP zawierający konfigurację i struktury danych.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować tutaj pełny algorytm MVA dla sieci:
        * wieloklasowej,
        * zamkniętej,
        * z różnymi typami węzłów (zgodnie z BCMP).
    - Uaktualnić:
        * `network.metrics` (średnie liczby klientów, czasy, throughput),
        * `ServiceCenter.mean_customers_per_class` itd.
    - Dobrać sensowne struktury pomocnicze (lokalne słowniki, tablice numpy).
    """
    # TODO: Codex – implementacja MVA (metoda SUM) dla sieci BCMP.
    raise NotImplementedError
