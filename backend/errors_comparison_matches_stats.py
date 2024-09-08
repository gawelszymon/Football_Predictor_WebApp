import sqlite3
import pandas as pd
import numpy as np

# Połączenie z bazą danych
conn_actual = sqlite3.connect('euro2024_matches_info.db')  # Baza danych z rzeczywistymi wynikami
conn_predicted = sqlite3.connect('predictions_euro2024_matches_info.db')  # Baza danych z przewidywaniami

# Załaduj dane rzeczywiste z tabeli 'matches'
query_actual = 'SELECT * FROM matches'
actual_df = pd.read_sql(query_actual, conn_actual)

# Załaduj dane przewidywane z tabeli 'predicted_matches'
query_predicted = 'SELECT * FROM predicted_matches'
predicted_df = pd.read_sql(query_predicted, conn_predicted)

# Zamknij połączenia z bazą danych
conn_actual.close()
conn_predicted.close()

# Konwersja kluczowych kolumn (team1_id, team2_id) na typ string w obu DataFrame'ach
actual_df['team1_id'] = actual_df['team1_id'].astype(str)
actual_df['team2_id'] = actual_df['team2_id'].astype(str)
predicted_df['team1_id'] = predicted_df['team1_id'].astype(str)
predicted_df['team2_id'] = predicted_df['team2_id'].astype(str)

# Scalanie danych rzeczywistych z przewidywaniami na podstawie team1_id i team2_id
merged_df = pd.merge(actual_df, predicted_df, on=['team1_id', 'team2_id'])

# Wyliczenie błędów (różnica między rzeczywistymi a przewidywanymi wartościami dla wybranych kolumn)
error_cols = ['team1_goals', 'team2_goals']  # Kolumny, dla których liczysz błędy

for col in error_cols:
    merged_df[f'{col}_error'] = merged_df[col] - merged_df[f'{col}_predicted']


def calculate_penalties_error(row):
    # Sprawdź, czy w rzeczywistości odbyły się karne
    if pd.notnull(row['team1_penalties']) and pd.notnull(row['team2_penalties']):
        # Upewnij się, że identyfikatory drużyn i penalty_winner są typu int -> str (bez .0)
        actual_winner = None

        # Określenie rzeczywistego zwycięzcy karnych
        if row['team1_penalties'] > row['team2_penalties']:
            actual_winner = str(int(row['team1_id']))  # Zwycięzca team1
        elif row['team1_penalties'] < row['team2_penalties']:
            actual_winner = str(int(row['team2_id']))  # Zwycięzca team2

        # Konwersja predicted_winner na str bez .0
        predicted_winner = str(int(float(row['penalty_winner']))) if pd.notnull(row['penalty_winner']) else None

        # Debugowanie - wyświetlanie wartości, które są porównywane
        print(f"team1_penalties: {row['team1_penalties']}, team2_penalties: {row['team2_penalties']}")
        print(f"actual_winner: {actual_winner}, predicted_winner: {predicted_winner}")

        # Porównanie rzeczywistego zwycięzcy z przewidywanym
        if actual_winner == predicted_winner:
            return 0  # Zgadza się, brak błędu
        else:
            return 1  # Błąd, przewidywany zwycięzca nie zgadza się
    elif pd.isnull(row['team1_penalties']) and pd.isnull(row['team2_penalties']):
        # Nie było rzutów karnych w rzeczywistości
        if row['penalty_shootout_needed'] == 1:
            return 1  # Błąd, przewidywano karne, ale ich nie było
        else:
            return 0  # Zgadza się, brak karnych i brak przewidywania karnych
    else:
        return np.nan  # W razie innych niespójności


# Konwersja typów dla identyfikatorów drużyn na str bez .0
merged_df['team1_id'] = merged_df['team1_id'].apply(lambda x: str(int(x)))
merged_df['team2_id'] = merged_df['team2_id'].apply(lambda x: str(int(x)))
merged_df['penalty_winner'] = merged_df['penalty_winner'].apply(lambda x: str(int(x)) if pd.notnull(x) else None)

# Zastosowanie funkcji do obliczania błędów karnych
merged_df['penalties_error'] = merged_df.apply(calculate_penalties_error, axis=1)

# Zapisz wynik do pliku CSV
merged_df.to_csv('errors_comparison_penalties.csv', index=False)

print("Porównanie zapisane w pliku 'errors_comparison_penalties.csv'.")
