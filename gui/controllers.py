"""Warstwa „kontrolerów”/logiki łączącej GUI z modelem BCMP.

Tutaj można umieścić funkcje/kontrolery, które:
- reagują na akcje użytkownika w GUI (zmiana parametru, kliknięcie „Przelicz”),
- modyfikują obiekt `BCMPNetwork`,
- wywołują obliczenia metody SUM/MVA,
- informują widoki o konieczności odświeżenia.
"""

from bcmp.network import BCMPNetwork
from bcmp import sum
from bcmp.simulation import TicketSimulation


class NetworkController:
    """Kontroler łączący GUI z modelem sieci BCMP.
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
        """
        sum.compute_network_metrics(self.network)
        self._notify_listeners()

    def tune_service_rates_for_rho(self, targets: dict[str, float]) -> None:
        """Skaluje stawki obsługi, aby zbliżyć się do docelowych wartości ρ."""

        if not self.network.metrics.visit_ratios:
            sum.compute_network_metrics(self.network)

        node_index = {node.id: idx for idx, node in enumerate(self.network.config.nodes)}
        visits = self.network.metrics.visit_ratios

        for node_id, target_rho in targets.items():
            if target_rho <= 0 or node_id not in self.network.nodes:
                continue

            idx = node_index.get(node_id)
            if idx is None:
                continue

            node = self.network.nodes[node_id]
            servers = node.config.servers or 1

            load_numerator = 0.0
            for class_id, visit_vector in visits.items():
                service_rate = node.config.service_rates_per_class.get(class_id)
                if service_rate is None or service_rate <= 0:
                    continue
                arrival = self.network.metrics.throughput_per_class.get(class_id, 0.0) * visit_vector[idx]
                load_numerator += arrival / service_rate

            current_rho = load_numerator / servers if servers > 0 else 0.0
            if current_rho == 0:
                continue

            scale = current_rho / target_rho
            for class_id, mu in node.config.service_rates_per_class.items():
                node.config.service_rates_per_class[class_id] = mu * scale

            for config_node in self.network.config.nodes:
                if config_node.id == node_id:
                    for class_id, mu in node.config.service_rates_per_class.items():
                        config_node.service_rates_per_class[class_id] = mu

        sum.compute_network_metrics(self.network)
        self._notify_listeners()

    # --- Symulacja -----------------------------------------------------------
    def toggle_simulation(self) -> None:
        if self.simulation is not None:
            self.simulation.toggle()

    def reset_simulation(self) -> None:
        if self.simulation is not None:
            self.simulation.reset()
