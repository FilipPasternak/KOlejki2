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

from bcmp.network import BCMPNetwork


class MainWindow:
    """Szkielet klasy głównego okna.

    Zadanie dla Codex:
    -------------------
    - Zamienić tę klasę na klasę dziedziczącą z odpowiedniej klasy frameworka GUI
      (np. `QMainWindow` w PyQt6).
    - Skonfigurować layout, menu, akcje, podwidoki (docki, zakładki itp.).
    - Zaimplementować mechanizmy aktualizacji widoków po zmianie modelu.
    """

    def __init__(self, network: BCMPNetwork) -> None:
        self.network = network
        # TODO: Codex – właściwa inicjalizacja komponentów GUI.
