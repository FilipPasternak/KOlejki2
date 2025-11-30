# Projekt: Sieć kolejkowa BCMP z metodą SUM (MVA)

Szkielet projektu w Pythonie pod system obsługi zgłoszeń modelowany jako sieć BCMP
(z minimum 5 systemami kolejkowymi i 4 klasami zgłoszeń), analizowany metodą SUM / MVA.

Kod jest jedynie *szkieletem* – brak implementacji algorytmów.
Ma służyć jako wejście dla modelu kodującego (np. Codex), który ma:
- uzupełnić klasy i funkcje zgodnie z docstringami i komentarzami,
- zaimplementować logikę BCMP i metody SUM,
- zbudować działające GUI (np. w PyQt6).

Struktura katalogów:

- `main.py` – punkt startowy aplikacji, spina konfigurację, logikę BCMP i GUI.
- `bcmp/` – logika modelu sieci BCMP i obliczeń MVA (SUM).
- `gui/` – warstwa interfejsu użytkownika.
