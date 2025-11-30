# Projekt: Sieć kolejkowa BCMP z metodą SUM (MVA)

Ten projekt prezentuje kompletny, uruchamialny prototyp aplikacji do analizy
zamkniętych, wieloklasowych sieci kolejkowych typu BCMP z użyciem algorytmu Mean
Value Analysis (metoda SUM) **oraz** wbudowaną symulację przepływu zgłoszeń w
czasie rzeczywistym. Warstwa logiczna jest napisana w Pythonie, a GUI oparto o
PyQt6.

## Wprowadzenie teoretyczne

### Modele BCMP

Sieci BCMP (Baskett–Chandy–Muntz–Palacios) pozwalają na analityczne obliczanie
średnich wielkości (liczby klientów, czasów przebywania, throughputu) w
złożonych sieciach kolejek przy założeniu określonych dyscyplin obsługi. W tym
projekcie przyjmujemy:

- **Zamkniętą** sieć: liczba klientów każdej klasy jest stała, nie ma napływu z
  zewnątrz.
- **Brak zmiany klasy**: klient zawsze pozostaje w swojej klasie (np. VIP,
  Standard itp.).
- **Obsługiwane typy węzłów**: FCFS (M/M/m), PS, IS, LCFS-PR.
- **Routing zależny od klasy**: każda klasa ma własną macierz prawdopodobieństw
  przejść między węzłami.

### Metoda SUM / Mean Value Analysis (MVA)

Algorytm MVA iteracyjnie zwiększa populację klientów od zera do pełnej liczby,
obliczając dla każdego stanu średnie czasy przebywania w węzłach oraz wynikający
z nich throughput. Kluczowe elementy obliczeń w implementacji:

1. **Współczynniki wizyt (visit ratios)** – wyliczane z macierzy routingu
   indywidualnie dla każdej klasy.
2. **Iteracje po stanach** – dla kolejnych wartości łącznej populacji
   obliczany jest średni czas przebywania w każdym węźle i średnia liczba
   klientów per węzeł i klasa.
3. **Czasy przebywania w węźle** – dla FCFS/PS/LCFS-PR użyto wzoru
   \(R_i = S_i (1 + L_i / m)\), dla IS przyjęto \(R_i = S_i\), gdzie
   \(S_i\) to średni czas obsługi, a \(m\) liczba serwerów.
4. **Throughput klas** – na końcu iteracji wyznaczany z równania
   \(X^{(k)} = N^{(k)} / \sum_i V_i^{(k)} R_i^{(k)}\), gdzie \(N^{(k)}\)
   to populacja klasy.

Wyniki (średnia liczba klientów, czasy odpowiedzi, throughput) zapisywane są w
`network.metrics` i prezentowane w GUI.

## Struktura katalogów

- `main.py` – punkt startowy aplikacji, spina konfigurację, logikę BCMP i GUI.
- `bcmp/` – logika modelu sieci BCMP i obliczeń MVA (SUM).
- `gui/` – warstwa interfejsu użytkownika.

## Uruchomienie aplikacji

1. **Utwórz i aktywuj środowisko (opcjonalnie)**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Zainstaluj zależności**

   ```bash
   pip install -r requirements.txt
   ```

3. **Uruchom aplikację z domyślną konfiguracją sieci**

```bash
python main.py
```

Po starcie otwiera się okno PyQt6 z trzema zakładkami:

- **Symulacja** – najważniejszy widok prezentujący w czasie rzeczywistym
  przepływ zgłoszeń pomiędzy węzłami (kolejki i liczba obsługiwanych zgłoszeń
  per węzeł) wraz z dziennikiem zdarzeń. Możesz zatrzymać lub zresetować
  symulację przyciskami na panelu sterującym.
- **Network** – konfiguracja sieci (węzły, klasy, routing) z możliwością
  edycji podstawowych parametrów.
- **Results** – wyniki analizy metodą SUM/MVA (średnie liczby klientów,
  czasy odpowiedzi i throughput).

Po starcie otwiera się okno PyQt6 prezentujące konfigurację sieci (węzły,
klasy, routing) oraz wyniki obliczeń. Zmiany parametrów w GUI można ponownie
przeliczyć z menu **Compute → Recompute** lub przyciskiem na pasku narzędzi.
