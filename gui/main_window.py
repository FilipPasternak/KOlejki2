"""Główne okno aplikacji (GUI).

To okno ma spinać poszczególne widoki:
- widok konfiguracji sieci (lista węzłów, klas, parametry),
- widok wyników (tabele/wizualizacje metryk),
- ewentualnie panel do modyfikacji parametrów i ponownego przeliczenia.

Zadanie dla Codex:
-------------------
- Zaimplementować klasę okna głównego w wybranym frameworku GUI (np. PyQt6).
- Zadbać o to, aby:
    * przechowywała odniesienie do `BCMPNetwork`,
    * udostępniała przyciski/akcje „Przelicz ponownie”,
    * odświeżała widoki po przeliczeniu metryk metodą SUM/MVA.
"""

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from bcmp.network import BCMPNetwork

from gui.controllers import NetworkController
from gui.network_view import NetworkView
from gui.results_view import ResultsView
from gui.simulation_view import SimulationView


class MainWindow(QMainWindow):
    """Główne okno aplikacji spinające widoki konfiguracji i wyników."""

    def __init__(self, network: BCMPNetwork, controller: NetworkController, simulation) -> None:
        super().__init__()

        self.network = network
        self.controller = controller
        self.simulation = simulation

        self.setWindowTitle("KOlejki2 – BCMP Network")
        self.resize(1000, 700)

        self._setup_actions()
        self._setup_central_widget()

        self.controller.add_listener(self.refresh_views)

    def _setup_actions(self) -> None:
        recompute_action = QAction("Recompute", self)
        recompute_action.triggered.connect(self.recompute_metrics)

        menubar = self.menuBar()
        compute_menu = menubar.addMenu("Compute")
        compute_menu.addAction(recompute_action)

        toolbar = self.addToolBar("Actions")
        toolbar.addAction(recompute_action)

    def _setup_central_widget(self) -> None:
        tabs = QTabWidget()

        self.simulation_view = SimulationView(self.network, self.simulation)
        self.network_view = NetworkView(self.network)
        self.results_view = ResultsView(self.network)

        tabs.addTab(self.simulation_view, "Symulacja")
        tabs.addTab(self.network_view, "Network")
        tabs.addTab(self.results_view, "Results")

        self.setCentralWidget(tabs)

    def recompute_metrics(self) -> None:
        """Wywołuje przeliczenie sieci i odświeża widoki."""

        self.controller.recompute_metrics()

    def refresh_views(self) -> None:
        self.network_view.refresh()
        self.results_view.refresh()
