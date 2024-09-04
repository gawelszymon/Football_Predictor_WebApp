import sqlite3

# Połączenie z bazą danych
db_path = 'euro1_teams2024.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Funkcja aktualizująca wartości team_id na podstawie nazwy drużyny
def update_team_id_by_name(updates):
    """
    Aktualizuje wartości w kolumnie 'team_id' na podstawie nazwy drużyny.
    :param updates: Słownik, gdzie kluczem jest nazwa drużyny, a wartością nowa wartość team_id.
    """
    for team_name, new_id in updates.items():
        cursor.execute("UPDATE teams SET team_id = ? WHERE team = ?", (new_id, team_name))
        print(f"Zaktualizowano team_id dla drużyny {team_name} na {new_id}")

# Przykład zmian wartości team_id
updates = {
    'Angola': 3585,
    'Argentina': 3437,
    'Australia': 3433,
    'Brazil': 3439,
    'Costa Rica': 8497,
    'Croatia': 3556,
    'Czech Republic': 3445,
    'Ecuador': 5750,
    'England': 3299,
    'France': 3377,
    'Germany': 3262,
    'Ghana': 3441,
    'Iran': 3582,
    'Italy': 3376,
    'Ivory Coast': 3591,
    'Japan': 3435,
    'Mexico': 6303,
    'Netherlands': 3379,
    'Paraguay': 3581,
    'Poland': 3442,
    'Portugal': 3300,
    'Saudi Arabia': 3807,
    'Serbia and Montenegro': 23380,
    'South Korea': 3589,
    'Spain': 3375,
    'Sweden': 3557,
    'Switzerland': 3384,
    'Togo': 3815,
    'Trinidad and Tobago': 7149,
    'Tunisia': 3670,
    'Ukraine': 3699,
    'United States': 3505,
    'South Africa': 3806,
    'Uruguay': 3449,
    'Greece': 3378,
    'Nigeria': 3444,
    'Algeria': 3614,
    'Slovenia': 3588,
    'Cameroon': 3434,
    'Serbia': 3438,
    'Denmark': 3436,
    'New Zealand': 9171,
    'Slovakia': 3503,
    'North Korea': 15457,
    'Honduras': 3432,
    'Chile': 3700,
    'Belgium': 3382,
    'Bosnia and Herzegovina': 3446,
    'Colombia': 3816,
    'Russia': 3448,
    'Egypt': 3672,
    'Iceland': 3574,
    'Morocco': 3575,
    'Panama': 3577,
    'Peru': 3584,
    'Senegal': 3499,
    'Canada': 3510,
    'Wales': 3864,
    'Qatar': 14162,
    'Austria': 3383,
    'Romania': 3447,
    'Turkey': 3381,
    'Republic of Ireland': 3509,
    'Albania': 3561,
    'Hungary': 3468,
    'Northern Ireland': 5674,
    'Scotland': 3380,
    'Finland': 3443,
    'North Macedonia': 5148,
    'Georgia': 3669
}

# Aktualizujemy wartości team_id
update_team_id_by_name(updates)

# Zatwierdzenie zmian
conn.commit()

# Zamknięcie połączenia
conn.close()