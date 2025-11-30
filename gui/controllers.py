"""Warstwa „kontrolerów”/logiki łączącej GUI z modelem BCMP.

Tutaj można umieścić funkcje/kontrolery, które:
- reagują na akcje użytkownika w GUI (zmiana parametru, kliknięcie „Przelicz”),
- modyfikują obiekt `BCMPNetwork`,
- wywołują obliczenia metody SUM/MVA,
- informują widoki o konieczności odświeżenia.
"""

from bcmp.network import BCMPNetwork
from bcmp import mva_sum
from bcmp.simulation import TicketSimulation


class NetworkController:
    """Kontroler łączący GUI z modelem sieci BCMP.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować metody:
        * do zmiany parametrów (np. populacji klas, czasów obsługi),
        * do wywołania `mva_sum.compute_network_metrics(network)`,
        * do powiadamiania widoków o zmianie danych (np. przez callbacki lub sygnały).
    """

    def __init__(self, network: BCMPNetwork, simulation: TicketSimulation | None = None) -> None:
        self.network = network
        self.simulation = simulation
        self._listeners = []

    def add_listener(self, callback) -> None:
        """Rejestruje funkcję wywoływaną po aktualizacji modelu."""

        self._listeners.append(callback)

    def _notify_listeners(self) -> None:
        for callback in self._listeners:
            callback()

    def recompute_metrics(self) -> None:
        """Przelicza metryki sieci i aktualizuje model.

        Zadanie dla Codex:
        -------------------
        - Wywołać funkcję MVA z `bcmp.mva_sum`.
        - Po przeliczeniu powiadomić widoki (np. przez mechanizm podpiętych callbacków).
        """
        mva_sum.compute_network_metrics(self.network)
        self._notify_listeners()

    # --- Symulacja -----------------------------------------------------------
    def toggle_simulation(self) -> None:
        if self.simulation is not None:
            self.simulation.toggle()

    def reset_simulation(self) -> None:
        if self.simulation is not None:
            self.simulation.reset()
