import sqlite3


# Funkcja do sprawdzania tabel i kolumn w bazie danych
def check_tables_and_columns(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Wyświetl dostępne tabele w bazie danych
    print(f"\nDostępne tabele w bazie danych {db_path}:")
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for table in tables:
        print(f"\nTabela: {table[0]}")

        # Wyświetl kolumny dla każdej tabeli
        print(f"Kolumny w tabeli {table[0]}:")
        columns = cursor.execute(f"PRAGMA table_info({table[0]});").fetchall()
        for column in columns:
            print(f"  {column[1]} (typ: {column[2]})")

    # Zamknięcie połączenia z bazą danych
    conn.close()


# Ścieżka do Twojej bazy danych
db_path2008 = 'euro_2008_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2012 = 'euro_2012_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2016 = 'euro_2016_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2020 = 'euro_2020_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2024 = 'euro_2024_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2006 = 'WC_2006_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2010 = 'WC_2010_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2018 = 'WC_2018_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych
db_path2022 = 'WC_2022_stats.db'  # Zmień na odpowiednią ścieżkę do bazy danych

# Wywołaj funkcję
check_tables_and_columns(db_path2006)
check_tables_and_columns(db_path2008)
check_tables_and_columns(db_path2010)
check_tables_and_columns(db_path2012)
check_tables_and_columns(db_path2016)
check_tables_and_columns(db_path2018)
check_tables_and_columns(db_path2020)
check_tables_and_columns(db_path2022)
check_tables_and_columns(db_path2024)

