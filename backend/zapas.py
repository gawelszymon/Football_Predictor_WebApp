import sqlite3
import pandas as pd

# Funkcja do wczytania tabeli i wyświetlenia jej kolumn
def show_columns(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5", conn)  # Pobranie kilku wierszy do sprawdzenia
    conn.close()
    return df.columns

# Wyświetlenie kolumn z tabeli 'club_stats' w bazie euro_2024_stats.db
euro_2024_db_path = 'euro_2024_stats.db'
columns = show_columns(euro_2024_db_path, 'club_stats')
print("Kolumny w tabeli 'club_stats' w euro_2024_stats.db:", columns)
