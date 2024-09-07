import sqlite3
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Funkcja ładowania danych z tabeli club_stats
def load_club_stats(db_path):
    conn = sqlite3.connect(db_path)
    club_stats = pd.read_sql_query("SELECT * FROM club_stats", conn)
    conn.close()
    return club_stats

# Funkcja ładowania danych z tabeli matches
def load_match_info(db_path):
    conn = sqlite3.connect(db_path)
    matches_info = pd.read_sql_query("SELECT * FROM matches", conn)
    conn.close()
    return matches_info

# Zsumowanie statystyk klubowych dla drużyn
def aggregate_team_stats(club_stats):
    team_stats = club_stats.groupby('team_id').sum().reset_index()
    return team_stats

# Połączenie statystyk drużynowych z danymi o meczach (z konwersją typów)
def merge_team_stats_with_matches(matches_info, team_stats):
    # Konwersja typów danych, aby upewnić się, że są zgodne
    matches_info['team1_id'] = matches_info['team1_id'].astype(int)
    matches_info['team2_id'] = matches_info['team2_id'].astype(int)
    team_stats['team_id'] = team_stats['team_id'].astype(int)

    # Połączenie danych
    matches_with_team_stats = matches_info.merge(team_stats, left_on='team1_id', right_on='team_id', suffixes=('_team1', '_team2'))
    matches_with_team_stats = matches_with_team_stats.merge(team_stats, left_on='team2_id', right_on='team_id', suffixes=('_team1', '_team2'))
    return matches_with_team_stats

# Funkcja trenowania modeli Random Forest dla drużyny 1 i drużyny 2
def train_random_forest(X, y_team1, y_team2):
    # Podział danych na zbiór treningowy i testowy
    X_train, X_test, y_train_team1, y_test_team1 = train_test_split(X, y_team1, test_size=0.2, random_state=42)
    _, _, y_train_team2, y_test_team2 = train_test_split(X, y_team2, test_size=0.2, random_state=42)

    # Model Random Forest dla drużyny 1
    rf_team1 = RandomForestRegressor(n_estimators=200, random_state=42)
    rf_team1.fit(X_train, y_train_team1)

    # Model Random Forest dla drużyny 2
    rf_team2 = RandomForestRegressor(n_estimators=200, random_state=42)
    rf_team2.fit(X_train, y_train_team2)

    # Przewidywanie wyników na zbiorze testowym
    y_pred_team1 = rf_team1.predict(X_test)
    y_pred_team2 = rf_team2.predict(X_test)

    # Zaokrąglanie wyników do liczb całkowitych
    y_pred_team1 = np.round(y_pred_team1).astype(int)
    y_pred_team2 = np.round(y_pred_team2).astype(int)

    # Wyliczenie MSE
    mse_team1 = mean_squared_error(y_test_team1, y_pred_team1)
    mse_team2 = mean_squared_error(y_test_team2, y_pred_team2)

    print(f'MSE dla drużyny 1: {mse_team1}')
    print(f'MSE dla drużyny 2: {mse_team2}')

    return rf_team1, rf_team2

# Przewidywanie wyników meczów na podstawie wytrenowanych modeli
def predict_match_outcomes(rf_team1, rf_team2, X):
    y_pred_team1 = np.round(rf_team1.predict(X)).astype(int)  # Zaokrąglone do całkowitych
    y_pred_team2 = np.round(rf_team2.predict(X)).astype(int)  # Zaokrąglone do całkowitych
    return y_pred_team1, y_pred_team2

# Funkcja sprawdzania, czy plik istnieje
def check_file_exists(db_path):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Plik {db_path} nie istnieje.")
    return db_path

# Lista turniejów
tournament_databases = [
    {'matches_db': 'worldcup2006_matches_info.db', 'stats_db': 'WC_2006_stats.db', 'name': 'WC 2006'},
    {'matches_db': 'euro2008_matches_info.db', 'stats_db': 'euro_2008_stats.db', 'name': 'Euro 2008'},
    {'matches_db': 'worldcup2010_matches_info.db', 'stats_db': 'WC_2010_stats.db', 'name': 'WC 2010'},
    {'matches_db': 'euro2012_matches_info.db', 'stats_db': 'euro_2012_stats.db', 'name': 'Euro 2012'},
    {'matches_db': 'euro2016_matches_info.db', 'stats_db': 'euro_2016_stats.db', 'name': 'Euro 2016'},
    {'matches_db': 'worldcup2018_matches_info.db', 'stats_db': 'WC_2018_stats.db', 'name': 'WC 2018'},
    {'matches_db': 'euro2020_matches_info.db', 'stats_db': 'euro_2020_stats.db', 'name': 'Euro 2020'},
    {'matches_db': 'worldcup2022_matches_info.db', 'stats_db': 'WC_2022_stats.db', 'name': 'WC 2022'},
]

# Przechowywanie wyników dla każdego turnieju
all_team_stats = []
all_match_stats = []

# Iteracja przez wszystkie bazy danych
for tournament in tournament_databases:
    try:
        print(f"Przetwarzanie turnieju: {tournament['name']}")

        # Ścieżki do baz danych - zmiana na 'backend'
        stats_db = check_file_exists(f"C:/Users/piete/Desktop/www_project/backend/{tournament['stats_db']}")
        matches_db = check_file_exists(f"C:/Users/piete/Desktop/www_project/backend/{tournament['matches_db']}")

        # Załaduj dane
        club_stats = load_club_stats(stats_db)
        matches_info = load_match_info(matches_db)

        # Zsumowanie statystyk drużynowych
        team_stats = aggregate_team_stats(club_stats)

        # Połączenie statystyk drużynowych z wynikami meczów
        matches_with_team_stats = merge_team_stats_with_matches(matches_info, team_stats)

        all_team_stats.append(team_stats)
        all_match_stats.append(matches_with_team_stats)

    except FileNotFoundError as e:
        print(f"Błąd: {e}")
        continue

# Połączenie wszystkich turniejów w jedną tabelę (tylko jeśli istnieją dane)
if all_match_stats:
    combined_match_stats = pd.concat(all_match_stats, ignore_index=True)
else:
    raise ValueError("Brak danych do przetwarzania - żadne pliki nie zostały załadowane.")

# Wyświetl wszystkie dostępne kolumny, aby zidentyfikować te, które powodują problemy
print("Dostępne kolumny w combined_match_stats:")
print(combined_match_stats.columns)

# Teraz usuń kolumny tekstowe lub niepotrzebne kolumny, które nie są numeryczne
# Na podstawie tego, co zobaczysz w powyższym kroku, usuń te kolumny
X = combined_match_stats.drop(columns=['team1_goals', 'team2_goals', 'team1_id', 'team2_id'])  # Usuń kolumny z wynikami i ID drużyn
y_team1 = combined_match_stats['team1_goals']  # Liczba goli dla drużyny 1
y_team2 = combined_match_stats['team2_goals']  # Liczba goli dla drużyny 2

# Trenowanie modeli Random Forest na połączonych danych
rf_team1, rf_team2 = train_random_forest(X, y_team1, y_team2)

# Przewidywanie wyników przyszłych meczów
y_pred_team1, y_pred_team2 = predict_match_outcomes(rf_team1, rf_team2, X)

# Wyświetlenie przewidywanych wyników
print(f'Przewidywane gole dla drużyny 1: {y_pred_team1}')
print(f'Przewidywane gole dla drużyny 2: {y_pred_team2}')
