"""Punkt startowy warstwy GUI.

Tutaj powinna znajdować się inicjalizacja frameworka GUI (np. PyQt6)
oraz uruchomienie głównego okna aplikacji.
"""

from PyQt6.QtWidgets import QApplication

from bcmp.network import BCMPNetwork
from gui.controllers import NetworkController
from gui.main_window import MainWindow


def run_gui(network: BCMPNetwork, simulation) -> None:
    """Uruchamia GUI PyQt6 z przekazanym obiektem `BCMPNetwork` i symulacją."""

    app = QApplication([])

    controller = NetworkController(network, simulation)
    window = MainWindow(network, controller, simulation)
    window.show()

    app.exec()
