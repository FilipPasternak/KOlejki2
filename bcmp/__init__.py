"""Pakiet z logiką sieci BCMP i obliczeniami metodą SUM (MVA).

Moduły:
- `config_schema` – definicje struktur konfiguracyjnych (węzły, klasy, routing, cała sieć).
- `classes` – reprezentacja klas klientów (zgłoszeń).
- `node` – reprezentacja pojedynczego węzła (systemu kolejkowego) BCMP.
- `routing` – pomocnicze struktury do opisu przejść między węzłami.
- `network` – klasa `BCMPNetwork` sklejająca całą sieć (węzły + klasy + routing).
- `mva_sum` – implementacja metody SUM / MVA dla sieci BCMP.
- `metrics` – struktury przechowujące wyniki obliczeń (L_i, R_i, X, itp.).
"""
