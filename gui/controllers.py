"""Warstwa „kontrolerów”/logiki łączącej GUI z modelem BCMP.

Tutaj można umieścić funkcje/kontrolery, które:
- reagują na akcje użytkownika w GUI (zmiana parametru, kliknięcie „Przelicz”),
- modyfikują obiekt `BCMPNetwork`,
- wywołują obliczenia metody SUM/MVA,
- informują widoki o konieczności odświeżenia.
"""

from bcmp.network import BCMPNetwork
from bcmp import mva_sum


class NetworkController:
    """Kontroler łączący GUI z modelem sieci BCMP.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować metody:
        * do zmiany parametrów (np. populacji klas, czasów obsługi),
        * do wywołania `mva_sum.compute_network_metrics(network)`,
        * do powiadamiania widoków o zmianie danych (np. przez callbacki lub sygnały).
    """

    def __init__(self, network: BCMPNetwork) -> None:
        self.network = network

    def recompute_metrics(self) -> None:
        """Przelicza metryki sieci i aktualizuje model.

        Zadanie dla Codex:
        -------------------
        - Wywołać funkcję MVA z `bcmp.mva_sum`.
        - Po przeliczeniu powiadomić widoki (np. przez mechanizm podpiętych callbacków).
        """
        mva_sum.compute_network_metrics(self.network)
        # TODO: Codex – powiadomienie widoków o zmianie.
