"""Punkt startowy warstwy GUI.

Tutaj powinna znajdować się inicjalizacja frameworka GUI (np. PyQt6)
oraz uruchomienie głównego okna aplikacji.
"""

from bcmp.network import BCMPNetwork


def run_gui(network: BCMPNetwork) -> None:
    """Uruchamia GUI i przekazuje do niego obiekt `BCMPNetwork`.

    Zadanie dla Codex:
    -------------------
    - Zaimplementować inicjalizację frameworka GUI:
        * np. dla PyQt6: stworzyć QApplication, główne okno itd.
    - Utworzyć instancję głównego okna (z modułu `gui.main_window`),
      przekazać mu obiekt `network` oraz ewentualne callbacki do przeliczeń.
    - Wywołać pętlę główną GUI (np. `app.exec()`).
    """
    # TODO: Codex – implementacja startu GUI na wybranym frameworku.
    raise NotImplementedError
