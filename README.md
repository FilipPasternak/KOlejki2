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

- **Zamkniętą** sieć: liczba klientów każdej klasy jest stała.
- **Brak zmiany klasy** – klient zawsze pozostaje w swojej klasie (VIP/STD/BATCH/MAINT).
- **Obsługiwane typy węzłów**: FCFS (M/M/m), PS, IS, LCFS-PR.
- **Routing zależny od klasy** – każda klasa ma własną macierz prawdopodobieństw
  przejść między węzłami.

### Metoda SUM / Mean Value Analysis (MVA)

Algorytm MVA iteracyjnie zwiększa populację klientów od zera do pełnej liczby,
obliczając dla każdego stanu średnie czasy przebywania, średnią liczbę klientów
w węzłach oraz throughput. Kluczowe elementy:

1. **Współczynniki wizyt (visit ratios)** – wyliczone z macierzy routingu dla każdej klasy.
2. **Iteracje po stanach** – od pustej sieci aż do pełnej populacji.
3. **Czasy przebywania** – dla FCFS/PS/LCFS-PR stosujemy
   \(R_i = S_i (1 + L_i / m)\); dla IS \(R_i = S_i\).
4. **Throughput** – \(X^{(k)} = N^{(k)} / \sum_i V_i^{(k)} R_i^{(k)}\).

Wyniki są przechowywane w `network.metrics` oraz wyświetlane w GUI.

## Struktura katalogów

- `main.py` – główny plik uruchamiający aplikację.
- `bcmp/` – implementacja modelu BCMP i MVA (SUM).
- `gui/` – warstwa graficzna aplikacji (PyQt6).

## Domyślna sieć kolejek (węzły i klasy) – interpretacja szpitalna

W projekcie zaszyto pięć węzłów kolejki oraz cztery klasy klientów.  
Aby routing był bardziej intuicyjny, domyślna sieć została osadzona
w narracji **szpitalnego centrum diagnostyczno-zabiegowego**.

### Węzły (oddziały)

- **INTAKE** – *Izba Przyjęć / Triage*  
  FCFS, 2 serwery  
  Pierwszy punkt kontaktu pacjenta. Zależnie od potrzeb może kierować go na
  diagnostykę (PRE_DIAG), badania (LAB) lub procedury (OPS).

- **PRE_DIAG** – *Szybka diagnostyka*  
  PS, 3 serwery  
  Wstępne badanie i decyzja o dalszych krokach. W zależności od klasy pacjent
  może trafić na zabieg (OPS), badania (LAB) albo wrócić do ponownego triage.

- **OPS** – *Procedury i zabiegi doraźne / planowe*  
  FCFS, 4 serwery  
  Realizuje drobne zabiegi oraz działania operacyjne. W przypadku wykrycia
  nagłych problemów pacjent może zostać przekazany do intensywnej terapii (ESC).

- **LAB** – *Laboratorium / Diagnostyka obrazowa*  
  IS, liczba serwerów nielimitowana  
  Modeluje szybkie i równoległe badania. Wyniki mogą kierować pacjenta ponownie
  na zabieg, na triage lub do dalszych badań.

- **ESC** – *Eskalacja kliniczna / Intensywna terapia (ICU)*  
  LCFS-PR, 1 serwer  
  Trafiają tu pacjenci z nagłym pogorszeniem stanu. Po stabilizacji wracają na
  triage (INTAKE), badania (LAB) lub zabieg (OPS) zależnie od klasy i routingu.

### Klasy klientów (typy pacjentów)

- **VIP** – pacjenci pilni, wysokiego ryzyka, często trafiają do ESC.  
- **STD** – standardowe przypadki szpitalne.  
- **BATCH** – pacjenci planowi (np. pakiet badań + zabieg).  
- **MAINT** – pacjenci przewlekli, wymagający cyklicznych kontroli i możliwej
  re-kwalifikacji w triage.

### Routing – interpretacja w kontekście szpitala

Routing jest w pełni zależny od klasy pacjenta. Przykładowe przepływy:

- **INTAKE → PRE_DIAG / OPS / LAB**  
  Rejestracja decyduje o pierwszym kroku: szybka diagnostyka, zabieg lub badania.
  Pacjenci BATCH i MAINT częściej trafiają bezpośrednio na LAB.

- **PRE_DIAG → OPS / LAB / INTAKE**  
  Wyniki szybkiej oceny mogą kierować pacjenta na zabieg, na badania lub
  wymuszać powrót do ponownego triage (np. z powodu niejednoznacznych objawów).

- **LAB → OPS / INTAKE**  
  Wyniki badań decydują o dalszych procedurach. Pacjenci mogą przechodzić przez
  LAB wielokrotnie.

- **OPS → ESC / INTAKE**  
  W trakcie zabiegów możliwe jest pogorszenie stanu (VIP/MAINT → ESC), lub
  powrót do triage po zakończonej procedurze.

- **ESC → LAB / OPS / INTAKE**  
  Pacjent po stabilizacji w intensywnej terapii wraca na dalszą diagnostykę lub
  ponowne zabiegi, w zależności od ścieżki klasy.

Tak zdefiniowany routing tworzy **zamkniętą pętlę szpitalną**, w której różne
typy pacjentów krążą między rejestracją, diagnostyką, zabiegami i intensywną
terapią, aż do osiągnięcia „punktu równowagi” modelowanego przez populację
zamkniętą.

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
  per węzeł) wraz z dziennikiem zdarzeń **oraz żywym wykresem długości kolejek**
  dla każdego węzła. Możesz zatrzymać lub zresetować symulację przyciskami na
  panelu sterującym.
- **Network** – konfiguracja sieci (węzły, klasy, routing) z możliwością
  edycji podstawowych parametrów oraz dostrajania stawek obsługi do docelowego
  wykorzystania serwerów (ρ) per węzeł.
- **Results** – wyniki analizy metodą SUM/MVA (średnie liczby klientów,
  czasy odpowiedzi i throughput) rozszerzone o metryki kolejki (Wq, W, Lq, L,
  ρ) liczone analitycznie i empirycznie (z symulacji) dla porównania.

Po starcie otwiera się okno PyQt6 prezentujące konfigurację sieci (węzły,
klasy, routing) oraz wyniki obliczeń. Zmiany parametrów w GUI można ponownie
przeliczyć z menu **Compute → Recompute** lub przyciskiem na pasku narzędzi.
