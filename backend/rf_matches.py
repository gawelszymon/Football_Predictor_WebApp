import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import sqlite3

# Funkcja do załadowania danych z bazy danych
def load_data(db_file, table_name):
    conn = sqlite3.connect(db_file)
    try:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        print(f"Błąd podczas wczytywania danych z {db_file}, tabela {table_name}: {e}")
        return None
    finally:
        conn.close()

# Funkcja do konwersji kolumn na odpowiedni typ tekstowy (string)
def convert_column_types(df):
    if df is not None:
        if 'team1_id' in df.columns:
            df['team1_id'] = df['team1_id'].astype(str)
        if 'team2_id' in df.columns:
            df['team2_id'] = df['team2_id'].astype(str)
        if 'team_id' in df.columns:
            df['team_id'] = df['team_id'].astype(str)
    return df

# Funkcja do łączenia danych meczowych z danymi klubowymi
def merge_data(matches, club_stats):
    matches = convert_column_types(matches)
    club_stats = convert_column_types(club_stats)

    team1_stats = club_stats.rename(columns=lambda x: f'{x}_team1')
    team2_stats = club_stats.rename(columns=lambda x: f'{x}_team2')

    try:
        merged_data = pd.merge(matches, team1_stats, left_on='team1_id', right_on='team_id_team1', how='left')
        merged_data = pd.merge(merged_data, team2_stats, left_on='team2_id', right_on='team_id_team2', how='left')
        return merged_data
    except KeyError as e:
        print(f"Błąd podczas łączenia danych: {e}")
        return None

# Funkcja do usunięcia kolumn nienumerycznych oraz tych, które są wynikami meczu (np. liczba bramek)
def remove_unnecessary_columns(df, is_prediction=False):
    df = df.drop(columns=['team1_penalties', 'team2_penalties'], errors='ignore')
    if is_prediction:
        # Usuwamy kolumny 'team1_goals' i 'team2_goals' podczas predykcji, ponieważ nie są one potrzebne w fazie predykcji
        df = df.drop(columns=['team1_goals', 'team2_goals'], errors='ignore')
    return df.select_dtypes(include=[np.number])

# Funkcja do trenowania modelu i przewidywania wyników
def train_rf_and_predict(tournament_databases, euro2024_matches, output_db):
    full_data = pd.DataFrame()

    for tournament in tournament_databases:
        print(f"Przetwarzanie danych dla {tournament['name']}...")
        matches = load_data(tournament['matches_db'], 'matches')
        club_stats = load_data(tournament['stats_db'], 'club_stats')

        if matches is None or club_stats is None:
            print(f"Błąd podczas przetwarzania danych dla {tournament['name']}")
            continue

        print(f"Podgląd danych meczowych dla {tournament['name']}:")
        print(matches.head())
        print(f"Podgląd danych klubowych dla {tournament['name']}:")
        print(club_stats.head())

        try:
            merged_data = merge_data(matches, club_stats)
            if merged_data is None:
                continue
            merged_data = remove_unnecessary_columns(merged_data)
            print(f"Dane po łączeniu dla {tournament['name']}:")
            print(merged_data.head())
            full_data = pd.concat([full_data, merged_data], ignore_index=True)
        except Exception as e:
            print(f"Błąd podczas łączenia danych dla {tournament['name']}: {e}")
            continue

    # Upewnij się, że dane mają odpowiednie kolumny
    if 'team1_goals' not in full_data.columns or 'team2_goals' not in full_data.columns:
        print("Brakuje kolumn 'team1_goals' lub 'team2_goals' w danych treningowych.")
        print(f"Dostępne kolumny w danych treningowych: {full_data.columns}")
        return

    euro2024_matches = convert_column_types(euro2024_matches)
    euro2024_matches = remove_unnecessary_columns(euro2024_matches, is_prediction=True)

    X = full_data.drop(columns=['team1_goals', 'team2_goals'], errors='ignore')
    y_team1 = full_data['team1_goals']
    y_team2 = full_data['team2_goals']

    X_train, X_test, y_train_team1, y_test_team1 = train_test_split(X, y_team1, test_size=0.2, random_state=42)
    _, _, y_train_team2, y_test_team2 = train_test_split(X, y_team2, test_size=0.2, random_state=42)

    rf_team1 = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_team2 = RandomForestRegressor(n_estimators=100, random_state=42)

    rf_team1.fit(X_train, y_train_team1)
    rf_team2.fit(X_train, y_train_team2)

    y_pred_team1 = np.round(rf_team1.predict(euro2024_matches)).astype(int)
    y_pred_team2 = np.round(rf_team2.predict(euro2024_matches)).astype(int)

    remisy_idx = np.where(y_pred_team1 == y_pred_team2)[0]

    penalty_team1 = np.round(np.random.uniform(3, 5, size=len(remisy_idx))).astype(int)
    penalty_team2 = np.round(np.random.uniform(3, 5, size=len(remisy_idx))).astype(int)

    conn = sqlite3.connect(output_db)
    results_df = pd.DataFrame({
        'team1_id': euro2024_matches['team1_id'],
        'team2_id': euro2024_matches['team2_id'],
        'team1_predicted_goals': y_pred_team1,
        'team2_predicted_goals': y_pred_team2,
        'team1_penalty_goals': [penalty_team1[i] if i in remisy_idx else None for i in range(len(y_pred_team1))],
        'team2_penalty_goals': [penalty_team2[i] if i in remisy_idx else None for i in range(len(y_pred_team2))]
    })
    results_df.to_sql('predicted_results', conn, if_exists='replace', index=False)
    conn.close()

    print(f"Wyniki zapisane w {output_db}")

# Przykład użycia funkcji
tournament_databases = [
    {'matches_db': 'worldcup2006_matches_info.db', 'stats_db': 'WC_2006_stats.db', 'name': 'WC 2006'},
    {'matches_db': 'euro2008_matches_info.db', 'stats_db': 'euro_2008_stats.db', 'name': 'Euro 2008'},
    {'matches_db': 'worldcup2010_matches_info.db', 'stats_db': 'WC_2010_stats.db', 'name': 'WC 2010'},
    {'matches_db': 'euro2016_matches_info.db', 'stats_db': 'euro_2016_stats.db', 'name': 'Euro 2016'},
    {'matches_db': 'worldcup2018_matches_info.db', 'stats_db': 'WC_2018_stats.db', 'name': 'WC 2018'},
    {'matches_db': 'euro2020_matches_info.db', 'stats_db': 'euro_2020_stats.db', 'name': 'Euro 2020'},
    {'matches_db': 'worldcup2022_matches_info.db', 'stats_db': 'WC_2022_stats.db', 'name': 'WC 2022'},
]

euro2024_matches = load_data('euro2024_matches_info.db', 'matches')

train_rf_and_predict(tournament_databases, euro2024_matches, 'predicted_results_euro_2024.db')
