# VisualGP-AStar


Aplikacija omogućava usporedni prikaz pretrage u realnom vremenu između Manhattan, Euklidske i genetski evoluirane heuristike.

## Funkcionalnosti

- Paralelni prikaz A* pretrage za Manhattan, Euklidsku i GP evoluiranu heuristiku.
- Interaktivno dodavanje i uklanjanje prepreka mišem sa automatskom sinhronizacijom na sva tri grida.
- Generisanje nasumičnih mapa sa 10%, 20% ili 30% prepreka.
- Prikaz matematičkog izraza i sintaksnog stabla najbolje jedinke.
- Grafički prikaz konvergencije fitness-a i komparativna tabela rezultata.

## Značenje boja na mreži

- Zelena: Startna tačka (S)
- Crvena: Ciljna tačka (G)
- Crna: Prepreka / Zid
- Svijetlo plava: Posijećeni čvorovi tokom pretrage
- Žuta: Pronađeni optimalni put
- Bijela: Slobodna polja

## Instalacija i pokretanje

Zahtjevi: Python 3.10+

Instalacija zavisnosti:
```bash
pip install -r requirements.txt
```

Struktura projekta:
```bash
visual_gp_astar/
├── main.py              # Ulazna tačka aplikacije
├── requirements.txt     # Zavisnosti projekta
├── README.md            # Dokumentacija
├── core/                # Logika i algoritmi
│   ├── grid.py          # Logika mreže
│   ├── a_star.py        # A* algoritam
│   └── gp_engine.py     # DEAP Genetsko Programiranje
├── ui/                  # Korisnički interfejs
│   ├── main_window.py   # Glavni prozor
│   ├── canvas_grid.py   # Crtanje i animacija mreže
│   ├── tree_viewer.py   # Prikaz GP stabla
│   └── charts.py        # Grafikon evolucije
└── utils/               # Pomoćni moduli
    └── evaluator.py     # Poređenje heuristika
```


