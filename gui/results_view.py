"""Widoki do prezentacji wyników obliczeń MVA (metoda SUM)."""

from bcmp.network import BCMPNetwork


class ResultsView:
    """Szkielet widoku prezentującego wyniki sieci BCMP.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować widget/okno pokazujące:
        * dla każdego węzła: średnią liczbę klientów (L_i, L_i^(k)),
        * średnie czasy odpowiedzi (R_i, R_i^(k)),
        * throughput per klasa,
        * ewentualnie wykresy (wykorzystanie węzłów, zależności od parametrów).

    - Zapewnić metodę do odświeżania widoku po ponownym przeliczeniu sieci.
    """

    def __init__(self, network: BCMPNetwork) -> None:
        self.network = network
        # TODO: Codex – inicjalizacja widgetów i logiki odświeżania.
