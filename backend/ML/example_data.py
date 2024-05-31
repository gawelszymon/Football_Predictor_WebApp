import pandas as pd

# Tworzenie przykładowych danych dla Tabeli Reprezentacji
data_reprezentacje = {
    'id': [1, 2, 3],
    'nazwa': ['Reprezentacja A', 'Reprezentacja B', 'Reprezentacja C'],
    'ranking_FIFA': [5, 10, 15],
    'wyniki_2_euro': [3, 2, 1],
    'wyniki_2_ms': [4, 1, 2],
    'srednia_wynikow_zawodnikow': [7.5, 6.8, 7.1],
    'ilosc_obroncow': [4, 5, 4],
    'ilosc_pomocnikow': [3, 2, 4],
    'ilosc_napastnikow': [3, 3, 2],
    'liczba_udzialow_w_Mistrzostwach_Swiata': [10, 8, 5],
    'liczba_udzialow_w_EURO': [8, 10, 7]
}

# Tworzenie przykładowych danych dla Tabeli Zawodników
data_zawodnicy = {
    'id': [1, 2, 3, 4, 5, 6],
    'imie_nazwisko': ['Zawodnik 1', 'Zawodnik 2', 'Zawodnik 3', 'Zawodnik 4', 'Zawodnik 5', 'Zawodnik 6'],
    'wiek': [28, 30, 22, 27, 24, 29],
    'wzrost': [180, 175, 178, 182, 185, 177],
    'srednia_ocen': [7.1, 6.8, 7.5, 7.0, 6.9, 7.2],
    'liga_UEFA_wspolczynnik': [1.1, 1.0, 1.2, 1.1, 0.9, 1.0],
    'gole': [10, 5, 7, 8, 4, 6],
    'asysty': [4, 6, 5, 3, 7, 4],
    'strzaly': [30, 25, 28, 32, 20, 27],
    'minuty': [1800, 1750, 1780, 1820, 1850, 1770],
    'kartki_zolte': [3, 2, 1, 4, 3, 2],
    'kartki_czerwone': [0, 1, 0, 0, 1, 0],
    'meczow': [20, 18, 22, 21, 19, 20],
    'sukcesywnosc_podania': [85.5, 82.3, 88.4, 86.7, 83.2, 84.9],
    'interwencje': [15, 18, 10, 12, 20, 17],
    'wartosc_rynkowa': [50, 45, 60, 55, 40, 48],
    'liczba_rozegranych_minut_w_sezonie': [1500, 1600, 1550, 1620, 1400, 1580],
    'forma': [7.0, 6.8, 7.2, 7.1, 6.9, 7.0],
    'liczba_sezonow_profesjonalnych': [10, 12, 4, 8, 6, 9],
    'szybkosc_km_h': [32.5, 30.2, 34.1, 31.8, 29.5, 33.0],
    'mentalnosc': [8, 7, 9, 8, 7, 8],
    'lider_zespolu_repka': [1, 0, 0, 1, 0, 0],
    'lider_zespolu_w_zespole_w_lidze': [1, 1, 0, 0, 1, 0],
    'reprezentacja_id': [1, 1, 2, 2, 3, 3]  # Przykładowe wartości klucza obcego
}

# Tworzenie przykładowych danych dla Bazy Danych Pseudodynamicznej
data_pseudo_reprezentacje = {
    'id': [1, 2, 3],
    'nazwa': ['Reprezentacja A', 'Reprezentacja B', 'Reprezentacja C'],
    'motywacja': [8, 7, 6],
    'srednia_wynikow_zawodnikow': [7.5, 6.8, 7.1],
    'wyniki_aktualnych_meczy': [1, 0, 1],
}

data_pseudo_zawodnicy = {
    'id': [1, 2, 3, 4, 5, 6],
    'imie_nazwisko': ['Zawodnik 1', 'Zawodnik 2', 'Zawodnik 3', 'Zawodnik 4', 'Zawodnik 5', 'Zawodnik 6'],
    'gole': [1, 0, 2, 1, 0, 1],
    'asysty': [0, 1, 1, 0, 2, 1],
    'strzaly': [5, 3, 4, 5, 2, 3],
    'minuty': [90, 85, 80, 90, 70, 85],
    'kartki_zolte': [0, 1, 0, 0, 1, 0],
    'kartki_czerwone': [0, 0, 0, 0, 0, 0],
    'meczow': [1, 1, 1, 1, 1, 1],
    'sukcesywnosc_podania': [85.0, 80.0, 90.0, 85.5, 75.0, 80.5],
    'interwencje': [2, 3, 1, 2, 4, 3],
    'liczba_rozegranych_minut_podczas_turnieju': [90, 85, 80, 90, 70, 85],
    'forma': [7.5, 6.8, 7.7, 7.3, 6.5, 7.0],
    'liczba_rozegranych_meczow_w_kadrze': [50, 45, 20, 35, 25, 40]
}

# Konwersja do DataFrame
df_reprezentacje = pd.DataFrame(data_reprezentacje)
df_zawodnicy = pd.DataFrame(data_zawodnicy)
df_pseudo_reprezentacje = pd.DataFrame(data_pseudo_reprezentacje)
df_pseudo_zawodnicy = pd.DataFrame(data_pseudo_zawodnicy)

# Zapis do plików CSV
df_reprezentacje.to_csv('reprezentacje.csv', index=False)
df_zawodnicy.to_csv('zawodnicy.csv', index=False)
df_pseudo_reprezentacje.to_csv('pseudo_reprezentacje.csv', index=False)
df_pseudo_zawodnicy.to_csv('pseudo_zawodnicy.csv', index=False)

df_reprezentacje.head(), df_zawodnicy.head(), df_pseudo_reprezentacje.head(), df_pseudo_zawodnicy.head()
