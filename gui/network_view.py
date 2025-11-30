"""Widoki związane z prezentacją struktury sieci BCMP.

Np. tabele/listy węzłów i klas, prosty graficzny rysunek sieci, itp.
"""

from bcmp.network import BCMPNetwork


class NetworkView:
    """Szkielet widoku prezentującego strukturę sieci.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować widget/okno pokazujące:
        * listę węzłów (z typem, liczbą serwerów, parametrami),
        * listę klas (z populacją, nazwą),
        * ewentualnie routing (np. w formie tabeli przejść).
    - Dodać możliwość prostych edycji parametrów (np. populacji klasy, czasu obsługi)
      oraz propagowania zmian do `BCMPNetwork`.
    """

    def __init__(self, network: BCMPNetwork) -> None:
        self.network = network
        # TODO: Codex – inicjalizacja widgetów GUI.
