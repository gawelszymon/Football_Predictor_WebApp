import sqlite3
import pandas as pd

# Połączenie z bazą danych
conn_actual = sqlite3.connect('euro_2024_stats.db')  # Baza danych z rzeczywistymi wartościami
conn_predicted = sqlite3.connect('euro_2024_predicted_stats.db')  # Baza danych z przewidywaniami

# Załaduj dane rzeczywiste
query_actual = 'SELECT * FROM tournament_stats'  # Dopasuj nazwę tabeli
actual_df = pd.read_sql(query_actual, conn_actual)

# Załaduj dane przewidywane
query_predicted = 'SELECT * FROM final_tournament_stats_predicted_rf_weighted'  # Dopasuj nazwę tabeli
predicted_df = pd.read_sql(query_predicted, conn_predicted)

# Zamknij połączenia z bazą danych
conn_actual.close()
conn_predicted.close()

# Dopasowanie kluczowych kolumn (team_id, position) i scalanie danych rzeczywistych z przewidywaniami
merged_df = pd.merge(actual_df, predicted_df, on=['team_id', 'position'], suffixes=('_actual', '_predicted'))

# Wyliczenie błędów (różnica między rzeczywistymi a przewidywanymi wartościami dla wybranych kolumn)
error_cols = ['minutes', 'yellow_cards', 'red_cards', 'goals', 'assists', 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches']  # Kolumny, dla których liczysz błędy

for col in error_cols:
    merged_df[f'{col}_error'] = merged_df[f'{col}_actual'] - merged_df[f'{col}_predicted']

# Zapisz wynik do pliku CSV
merged_df.to_csv('errors_comparison.csv', index=False)

print("Porównanie zapisane w pliku 'errors_comparison.csv'.")
