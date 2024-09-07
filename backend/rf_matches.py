import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np


# Funkcja do wczytywania tabel z bazy danych
def load_full_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Funkcja do przygotowania danych meczowych i klubowych
def merge_club_stats_for_prediction(matches, club_stats):
    matches['team1_id'] = matches['team1_id'].astype(int)
    matches['team2_id'] = matches['team2_id'].astype(int)
    club_stats['team_id'] = club_stats['team_id'].astype(int)

    team1_stats = club_stats.rename(columns=lambda col: f"team1_{col}" if col != 'team_id' else col)
    team2_stats = club_stats.rename(columns=lambda col: f"team2_{col}" if col != 'team_id' else col)

    merged_df = matches.merge(team1_stats, left_on='team1_id', right_on='team_id', how='left')
    merged_df = merged_df.merge(team2_stats, left_on='team2_id', right_on='team_id', how='left')

    return merged_df


# Funkcja do trenowania modelu Random Forest
def train_rf_model(X, y):
    rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
    rf_model.fit(X, y)
    return rf_model


# Funkcja do przewidywania wyników regulaminowego czasu gry
def predict_euro_2024_matches(rf_team1, rf_team2, club_stats_2024):
    club_stats_2024_team1 = club_stats_2024.rename(columns={'goals': 'team1_goals_y'})
    club_stats_2024_team2 = club_stats_2024.rename(columns={'goals': 'team2_goals_y'})

    club_stats_2024_team1 = club_stats_2024_team1.rename(
        columns=lambda col: f"team1_{col}" if col in ['ranking', 'value', 'appearances', 'assists'] else col)
    club_stats_2024_team2 = club_stats_2024_team2.rename(
        columns=lambda col: f"team2_{col}" if col in ['ranking', 'value', 'appearances', 'assists'] else col)

    X_euro_2024 = pd.concat(
        [club_stats_2024_team1[['team1_ranking', 'team1_value', 'team1_appearances', 'team1_goals_y', 'team1_assists']],
         club_stats_2024_team2[
             ['team2_ranking', 'team2_value', 'team2_appearances', 'team2_goals_y', 'team2_assists']]], axis=1)

    team1_goals_pred = np.round(rf_team1.predict(X_euro_2024)).astype(int)
    team2_goals_pred = np.round(rf_team2.predict(X_euro_2024)).astype(int)
    return team1_goals_pred, team2_goals_pred


# Funkcja do przewidywania wyników rzutów karnych (penalty shootout) - z ograniczeniami
def predict_penalty_shootouts(rf_penalty, X_penalty):
    # Symulujemy liczbę bramek w rzutach karnych dla obu drużyn
    penalty_goals_pred_team1 = np.clip(np.round(rf_penalty.predict(X_penalty)).astype(int), 0, 5)
    penalty_goals_pred_team2 = np.clip(np.round(rf_penalty.predict(X_penalty)).astype(int), 0, 5)

    # Zapewniamy, że wynik jest możliwy w rzeczywistej serii rzutów karnych
    for i in range(len(penalty_goals_pred_team1)):
        if penalty_goals_pred_team1[i] == penalty_goals_pred_team2[i]:
            # Losowo zwiększamy wynik jednej z drużyn, aby uniknąć remisu
            if penalty_goals_pred_team1[i] < 5:
                penalty_goals_pred_team1[i] += 1
            else:
                penalty_goals_pred_team2[i] -= 1  # Zmniejszamy drugą drużynę, aby uniknąć remisu przy 5:5

        # Sprawdzamy najszybszy możliwy wynik 3:0
        if penalty_goals_pred_team1[i] == 3 and penalty_goals_pred_team2[i] == 0:
            continue  # Taki wynik jest ok
        elif penalty_goals_pred_team2[i] == 3 and penalty_goals_pred_team1[i] == 0:
            continue  # Taki wynik jest ok

    return penalty_goals_pred_team1, penalty_goals_pred_team2


# Funkcja do zapisu przewidywanych wyników do nowej bazy danych
def save_predictions_to_new_db(predictions, new_db_path):
    conn = sqlite3.connect(new_db_path)
    predictions.to_sql('predicted_matches', conn, if_exists='replace', index=False)
    conn.close()

# Funkcja do wczytywania tabel z bazy danych
def load_full_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Funkcja do przygotowania danych meczowych i klubowych
def merge_club_stats_for_prediction(matches, club_stats):
    matches['team1_id'] = matches['team1_id'].astype(int)
    matches['team2_id'] = matches['team2_id'].astype(int)
    club_stats['team_id'] = club_stats['team_id'].astype(int)

    team1_stats = club_stats.rename(columns=lambda col: f"team1_{col}" if col != 'team_id' else col)
    team2_stats = club_stats.rename(columns=lambda col: f"team2_{col}" if col != 'team_id' else col)

    merged_df = matches.merge(team1_stats, left_on='team1_id', right_on='team_id', how='left')
    merged_df = merged_df.merge(team2_stats, left_on='team2_id', right_on='team_id', how='left')

    return merged_df


# Funkcja do trenowania modelu Random Forest
def train_rf_model(X, y):
    rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
    rf_model.fit(X, y)
    return rf_model


# Funkcja do przewidywania wyników regulaminowego czasu gry
def predict_euro_2024_matches(rf_team1, rf_team2, club_stats_2024):
    club_stats_2024_team1 = club_stats_2024.rename(columns={'goals': 'team1_goals_y'})
    club_stats_2024_team2 = club_stats_2024.rename(columns={'goals': 'team2_goals_y'})

    club_stats_2024_team1 = club_stats_2024_team1.rename(
        columns=lambda col: f"team1_{col}" if col in ['ranking', 'value', 'appearances', 'assists'] else col)
    club_stats_2024_team2 = club_stats_2024_team2.rename(
        columns=lambda col: f"team2_{col}" if col in ['ranking', 'value', 'appearances', 'assists'] else col)

    X_euro_2024 = pd.concat(
        [club_stats_2024_team1[['team1_ranking', 'team1_value', 'team1_appearances', 'team1_goals_y', 'team1_assists']],
         club_stats_2024_team2[
             ['team2_ranking', 'team2_value', 'team2_appearances', 'team2_goals_y', 'team2_assists']]], axis=1)

    team1_goals_pred = np.round(rf_team1.predict(X_euro_2024)).astype(int)
    team2_goals_pred = np.round(rf_team2.predict(X_euro_2024)).astype(int)
    return team1_goals_pred, team2_goals_pred


# Funkcja do przewidywania wyników rzutów karnych (penalty shootout)
def predict_penalty_shootouts(rf_penalty, X_penalty):
    # Przewidujemy wynik dla obu drużyn, ale musimy korygować niemożliwe wartości
    penalty_goals_pred_team1 = np.clip(np.round(rf_penalty.predict(X_penalty)).astype(int), 0, 5)
    penalty_goals_pred_team2 = np.clip(np.round(rf_penalty.predict(X_penalty)).astype(int), 0, 5)

    # Zabezpieczenie przed niemożliwymi wynikami
    for i in range(len(penalty_goals_pred_team1)):
        # Minimalny wynik dla zwycięstwa to 3:0, 4:1, 5:4 itp.
        if penalty_goals_pred_team1[i] < 3 and penalty_goals_pred_team2[i] == 0:
            penalty_goals_pred_team1[i] = 3
        elif penalty_goals_pred_team1[i] == penalty_goals_pred_team2[i]:
            # Remis — musimy dodać bramkę, aby wyłonić zwycięzcę
            penalty_goals_pred_team1[i] = 5
            penalty_goals_pred_team2[i] = 4

        # Jeśli wynik jest 4:3 lub podobny, zmień na wynik rozstrzygający
        if penalty_goals_pred_team1[i] == 4 and penalty_goals_pred_team2[i] == 3:
            penalty_goals_pred_team1[i] = 5
            penalty_goals_pred_team2[i] = 3

        # Poprawienie minimalnej przewagi, aby wyniki były poprawne
        if penalty_goals_pred_team1[i] - penalty_goals_pred_team2[i] < 2 and penalty_goals_pred_team1[i] >= 3:
            penalty_goals_pred_team1[i] = penalty_goals_pred_team2[i] + 2

    return penalty_goals_pred_team1, penalty_goals_pred_team2



# Funkcja do zapisu przewidywanych wyników do nowej bazy danych
def save_predictions_to_new_db(predictions, new_db_path):
    conn = sqlite3.connect(new_db_path)
    predictions.to_sql('predicted_matches', conn, if_exists='replace', index=False)
    conn.close()


# Główna funkcja do trenowania modelu i przewidywania wyników
def run_rf_predictions_for_euro_2024(tournaments, new_db_path):
    combined_X = []
    combined_y_team1 = []
    combined_y_team2 = []
    combined_penalty_matches = []

    # Wczytujemy dane z przeszłych turniejów
    for tournament in tournaments:
        print(f"\nProcessing {tournament['name']}...")

        club_stats = load_full_table(tournament['stats_db'], 'club_stats')
        matches = load_full_table(tournament['matches_db'], 'matches')

        merged_data = merge_club_stats_for_prediction(matches, club_stats)

        features = ['team1_ranking', 'team1_value', 'team1_appearances', 'team1_goals_y', 'team1_assists',
                    'team2_ranking', 'team2_value', 'team2_appearances', 'team2_goals_y', 'team2_assists']

        X = merged_data[features]
        y_team1 = merged_data['team1_goals_x'].astype(int)
        y_team2 = merged_data['team2_goals_x'].astype(int)

        penalty_matches = merged_data[~merged_data['team1_penalties'].isna() | ~merged_data['team2_penalties'].isna()]
        penalty_features = ['team1_ranking', 'team1_value', 'team1_appearances', 'team1_goals_y', 'team1_assists',
                            'team2_ranking', 'team2_value', 'team2_appearances', 'team2_goals_y', 'team2_assists']
        penalty_X = penalty_matches[penalty_features]

        combined_X.append(X)
        combined_y_team1.append(y_team1)
        combined_y_team2.append(y_team2)
        combined_penalty_matches.append(penalty_X)

    X_combined = pd.concat(combined_X)
    y_team1_combined = pd.concat(combined_y_team1)
    y_team2_combined = pd.concat(combined_y_team2)
    penalty_X_combined = pd.concat(combined_penalty_matches)

    rf_team1 = train_rf_model(X_combined, y_team1_combined)
    rf_team2 = train_rf_model(X_combined, y_team2_combined)
    rf_penalty = train_rf_model(penalty_X_combined, y_team1_combined[:len(penalty_X_combined)])

    club_stats_2024 = load_full_table('euro_2024_stats.db', 'club_stats')

    team1_goals_pred, team2_goals_pred = predict_euro_2024_matches(rf_team1, rf_team2, club_stats_2024)

    penalty_shootout_needed = team1_goals_pred == team2_goals_pred

    # Inicjalizujemy wyniki rzutów karnych jako NaN
    penalty_goals_team1_pred = np.full(len(team1_goals_pred), np.nan)
    penalty_goals_team2_pred = np.full(len(team2_goals_pred), np.nan)

    # Przewidujemy rzuty karne tylko dla meczów, które tego potrzebują
    if penalty_shootout_needed.any():
        penalty_X_filtered = penalty_X_combined.iloc[:len(penalty_shootout_needed)][penalty_shootout_needed]

        if not penalty_X_filtered.empty:
            penalty_goals_team1_pred[penalty_shootout_needed], penalty_goals_team2_pred[
                penalty_shootout_needed] = predict_penalty_shootouts(rf_penalty, penalty_X_filtered)

    # Sprawdzamy długości kolumn
    print(f"Length check: team1_goals_pred: {len(team1_goals_pred)}, team2_goals_pred: {len(team2_goals_pred)}, "
          f"penalty_goals_team1_pred: {len(penalty_goals_team1_pred)}, penalty_goals_team2_pred: {len(penalty_goals_team2_pred)}")

    # Upewniamy się, że wszystkie kolumny mają taką samą długość
    if len(team1_goals_pred) == len(team2_goals_pred) == len(penalty_goals_team1_pred) == len(penalty_goals_team2_pred):
        predictions = pd.DataFrame({
            'team1_id': club_stats_2024['team_id'],
            'team1_goals_predicted': team1_goals_pred,
            'team2_id': club_stats_2024['team_id'],
            'team2_goals_predicted': team2_goals_pred,
            'penalty_shootout': penalty_shootout_needed.astype(int),
            'penalty_goals_team1_pred': penalty_goals_team1_pred,
            'penalty_goals_team2_pred': penalty_goals_team2_pred
        })

        save_predictions_to_new_db(predictions, new_db_path)
    else:
        print("Error: Columns have mismatched lengths and cannot be combined into a DataFrame.")


# Przykładowa lista turniejów do trenowania modelu
tournaments = [
    {"name": "WC 2018", "stats_db": "WC_2018_stats.db", "matches_db": "worldcup2018_matches_info.db"},
    {"name": "WC 2022", "stats_db": "WC_2022_stats.db", "matches_db": "worldcup2022_matches_info.db"},
]

new_db_path = 'predictions_euro2024_matches_info.db'
run_rf_predictions_for_euro_2024(tournaments, new_db_path)
