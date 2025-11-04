BrawlStarsBackend/
│
├── app.py                  ← główny plik uruchamiający serwer Flask
├── config.py               ← konfiguracja połączenia z bazą danych
│
├── models/
│   ├── __init__.py         ← wspólna instancja SQLAlchemy
│   ├── player.py           ← model gracza (Player)
│   └── brawler.py          ← model postaci (Brawler)
│
└── routes/
    ├── __init__.py
    ├── player_routes.py    ← endpointy do zarządzania graczami
    └── brawler_routes.py   ← endpointy do zarządzania brawlerami
