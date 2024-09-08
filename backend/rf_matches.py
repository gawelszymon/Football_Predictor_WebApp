import random
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


# Funkcja do przygotowania danych meczowych i klubowych z poprawnym przypisaniem team1 i team2
def merge_club_stats_for_prediction(matches, club_stats):
    matches.loc[:, 'team1_id'] = matches['team1_id'].astype(int)
    matches.loc[:, 'team2_id'] = matches['team2_id'].astype(int)
    club_stats.loc[:, 'team_id'] = club_stats['team_id'].astype(int)

    # Agregujemy statystyki dla drużyny, żeby nie było powtórzeń
    aggregated_stats = club_stats.groupby('team_id').agg({
        'ranking': 'mean',
        'clean_sheets': 'sum',
        'conceded_goals': 'sum',
        'value': 'sum',
        'appearances': 'sum',
        'goals': 'sum',
        'assists': 'sum',
        'yellow_cards': 'sum',
        'red_cards': 'sum',
        'minutes_played': 'sum'
    }).reset_index()

    # Dołączanie statystyk dla team1
    team1_stats = aggregated_stats.rename(columns=lambda col: f"team1_{col}" if col != 'team_id' else col)
    merged_df = matches.merge(team1_stats, left_on='team1_id', right_on='team_id', how='left')

    # Dołączanie statystyk dla team2
    team2_stats = aggregated_stats.rename(columns=lambda col: f"team2_{col}" if col != 'team_id' else col)
    merged_df = merged_df.merge(team2_stats, left_on='team2_id', right_on='team_id', how='left')

    # Usuwamy zbędne kolumny 'team_id_x' i 'team_id_y', które wynikają z podwójnego merge
    merged_df.drop(columns=['team_id_x', 'team_id_y'], inplace=True)

    return merged_df


# Funkcja do trenowania modelu Random Forest
def train_rf_model(X, y):
    rf_model = RandomForestRegressor(n_estimators=2000, max_depth=30, min_samples_split=10, min_samples_leaf=5, bootstrap=False, random_state=42)
    rf_model.fit(X, y)
    return rf_model


def predict_euro_2024_matches(rf_team1, rf_team2, club_stats_2024, matches_2024):
    # Przygotowanie danych dla predykcji wyników meczów Euro 2024
    X_2024 = merge_club_stats_for_prediction(matches_2024, club_stats_2024)
    features_team1 = ['team1_appearances', 'team1_goals_y', 'team1_assists', 'team1_ranking', 'team1_value']
    features_team2 = ['team2_appearances', 'team2_goals_y', 'team2_assists', 'team2_ranking', 'team2_value']
    X_euro_2024 = X_2024[features_team1 + features_team2]

    # Predykcja na podstawie Random Forest
    team1_goals_pred = rf_team1.predict(X_euro_2024)
    team2_goals_pred = rf_team2.predict(X_euro_2024)

    # Obliczanie różnicy w statystykach między drużynami (np. na podstawie wartości zespołu lub rankingu)
    team1_advantage = X_2024['team1_value'] - X_2024['team2_value']  # Możesz to zmienić na inną statystykę
    advantage_factor = 0.0000000006  # Czynnik, który decyduje, jak duży wpływ mają różnice statystyk na wynik

    # Jeśli drużyna 1 ma przewagę w statystykach, zwiększamy jej przewidywaną liczbę goli
    team1_goals_pred += advantage_factor * team1_advantage
    team2_goals_pred -= advantage_factor * team1_advantage  # Zmniejszamy wynik dla przeciwnika

    # Zaokrąglamy wyniki do liczb całkowitych i upewniamy się, że wynik goli nie jest ujemny
    team1_goals_pred = np.clip(np.round(team1_goals_pred), 0, None).astype(int)
    team2_goals_pred = np.clip(np.round(team2_goals_pred), 0, None).astype(int)

    return team1_goals_pred, team2_goals_pred


# Funkcja do zapisu przewidywanych wyników do nowej bazy danych
def save_predictions_to_new_db(predictions, new_db_path):
    conn = sqlite3.connect(new_db_path)
    predictions.to_sql('predicted_matches', conn, if_exists='replace', index=False)
    conn.close()

# Funkcja do przewidywania wyników rzutów karnych
def predict_penalty_winner(rf_penalty, X_penalty):
    penalty_features = ['team1_appearances', 'team1_goals_y', 'team1_assists', 'team1_ranking', 'team1_value',
                        'team2_appearances', 'team2_goals_y', 'team2_assists', 'team2_ranking', 'team2_value']
    X_penalty_filtered = X_penalty[penalty_features]

    # Przewidywanie zwycięzcy rzutów karnych
    penalty_winner = np.round(rf_penalty.predict(X_penalty_filtered)).astype(int)
    return penalty_winner


def run_weighted_rf_predictions_for_euro_2024(tournaments, new_db_path):
    rf_models_team1 = []
    rf_models_team2 = []
    tournament_weights = []

    # Zmienna kontrolująca maksymalną wagę dla modelu o MSE równym 0
    max_weight = 1000

    # Wczytujemy dane z każdego turnieju, trenujemy model, liczymy MSE i zapisujemy wagi
    for tournament in tournaments:
        print(f"\nProcessing {tournament['name']}...")

        # Ładowanie danych z turnieju
        club_stats = load_full_table(tournament['stats_db'], 'club_stats')
        matches = load_full_table(tournament['matches_db'], 'matches')

        merged_data = merge_club_stats_for_prediction(matches, club_stats)

        # Wybieramy odpowiednie cechy do trenowania
        features = ['team1_appearances', 'team1_goals_y', 'team1_assists', 'team1_ranking', 'team1_value',
                    'team2_appearances', 'team2_goals_y', 'team2_assists', 'team2_ranking', 'team2_value']

        X = merged_data[features]
        y_team1 = merged_data['team1_goals_x'].astype(int)
        y_team2 = merged_data['team2_goals_x'].astype(int)

        # Trenujemy modele
        rf_team1 = train_rf_model(X, y_team1)
        rf_team2 = train_rf_model(X, y_team2)

        # Ocena modelu na danych treningowych za pomocą MSE
        team1_predictions = np.round(rf_team1.predict(X)).astype(int)
        team2_predictions = np.round(rf_team2.predict(X)).astype(int)

        mse_team1 = np.mean((y_team1 - team1_predictions) ** 2)
        mse_team2 = np.mean((y_team2 - team2_predictions) ** 2)

        # Obliczamy średnią MSE dla turnieju
        average_mse = (mse_team1 + mse_team2) / 2

        # Obliczamy wagę dla turnieju na podstawie średniej MSE, jeśli MSE wynosi 0, ustalamy maksymalną wagę
        if average_mse == 0:
            tournament_weight = max_weight
        else:
            tournament_weight = 1 / average_mse

        # Drukowanie wag dla turnieju
        print(f"Turniej: {tournament['name']}")
        print(f"  Średnia MSE: {average_mse}")
        print(f"  Waga turnieju: {tournament_weight}\n")

        # Przechowujemy modele i ich wspólną wagę
        rf_models_team1.append((rf_team1, tournament_weight))
        rf_models_team2.append((rf_team2, tournament_weight))

    # Ładowanie danych dla Euro 2024
    club_stats_2024 = load_full_table('euro_2024_stats.db', 'club_stats')
    matches_2024 = load_full_table('euro2024_matches_info.db', 'matches')

    # Przewidywania dla Euro 2024 na podstawie trenowanych modeli
    final_team1_predictions = np.zeros(len(matches_2024))
    final_team2_predictions = np.zeros(len(matches_2024))
    total_weights = 0

    for (rf_team1, weight), (rf_team2, _) in zip(rf_models_team1, rf_models_team2):
        team1_pred_2024, team2_pred_2024 = predict_euro_2024_matches(rf_team1, rf_team2, club_stats_2024, matches_2024)
        final_team1_predictions += team1_pred_2024 * weight
        final_team2_predictions += team2_pred_2024 * weight
        total_weights += weight

    # Normalizujemy przewidywania na podstawie sumy wag
    final_team1_predictions /= total_weights
    final_team2_predictions /= total_weights

    # Zaokrąglamy przewidywania do liczb całkowitych
    final_team1_predictions = np.round(final_team1_predictions).astype(int)
    final_team2_predictions = np.round(final_team2_predictions).astype(int)

    # Sprawdzamy, które mecze zakończyły się remisem
    penalty_shootout_needed = final_team1_predictions == final_team2_predictions

    # Filtrowanie meczów, które skończyły się remisem
    penalty_matches = matches_2024[penalty_shootout_needed]

    # Przypisujemy statystyki tylko dla meczów, które zakończyły się remisem
    penalty_X = merge_club_stats_for_prediction(penalty_matches, club_stats_2024)

    # Trenujemy model na rzutach karnych
    rf_penalty = train_rf_model(X, y_team1)  # Możemy użyć tych samych danych co wcześniej do treningu modelu

    penalty_winners = np.full(len(final_team1_predictions), np.nan)
    if penalty_shootout_needed.any():
        predicted_winner = predict_penalty_winner(rf_penalty, penalty_X)

        # Zamiana wartości 1 lub 2 na team1_id lub team2_id
        penalty_winners[penalty_shootout_needed] = np.where(
            predicted_winner == 1,
            matches_2024.loc[penalty_shootout_needed, 'team1_id'],
            matches_2024.loc[penalty_shootout_needed, 'team2_id']
        )

    # Zapisujemy wyniki
    predictions = pd.DataFrame({
        'team1_id': matches_2024['team1_id'],
        'team1_goals_predicted': final_team1_predictions,
        'team2_id': matches_2024['team2_id'],
        'team2_goals_predicted': final_team2_predictions,
        'penalty_shootout_needed': penalty_shootout_needed.astype(int),
        'penalty_winner': penalty_winners
    })

    save_predictions_to_new_db(predictions, new_db_path)


# Przykładowa lista turniejów do trenowania modelu
tournaments = [
    {"name": "WC 2006", "stats_db": "WC_2006_stats.db", "matches_db": "worldcup2006_matches_info.db"},
    {"name": "WC 2010", "stats_db": "WC_2010_stats.db", "matches_db": "worldcup2010_matches_info.db"},
    {"name": "WC 2014", "stats_db": "WC_2014_stats.db", "matches_db": "worldcup2014_matches_info.db"},
    {"name": "WC 2018", "stats_db": "WC_2018_stats.db", "matches_db": "worldcup2018_matches_info.db"},
    {"name": "WC 2022", "stats_db": "WC_2022_stats.db", "matches_db": "worldcup2022_matches_info.db"},
    {"name": "euro 2008", "stats_db": "euro_2008_stats.db", "matches_db": "euro2008_matches_info.db"},
    {"name": "euro 2012", "stats_db": "euro_2012_stats.db", "matches_db": "euro2012_matches_info.db"},
    {"name": "euro 2016", "stats_db": "euro_2016_stats.db", "matches_db": "euro2016_matches_info.db"},
    {"name": "euro 2020", "stats_db": "euro_2020_stats.db", "matches_db": "euro2020_matches_info.db"},
]

new_db_path = 'predictions_euro2024_matches_info.db'
run_weighted_rf_predictions_for_euro_2024(tournaments, new_db_path)
