import requests
from bs4 import BeautifulSoup
import unidecode
import sqlite3
import pandas as pd

def get_countries_rating():
    url = "https://www.sofascore.com/api/v1/rankings/type/2"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Nie udało się pobrać danych, status code: {response.status_code}")
        return None

    try:
        data = response.json()  # Sprawdzenie czy odpowiedź to JSON
    except ValueError:
        print("Odpowiedź serwera nie jest w formacie JSON")
        return None

    rating_dict = {}
    for ranking in data.get('rankings', []):
        team_name = ranking['team']['name']
        points = ranking['points']
        rating_dict[team_name] = points
    return rating_dict


# Funkcja pobierająca informacje o zespołach z Sofascore
def get_teams_info():
    url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/56953/standings/total"
    response = requests.get(url)

    # Sprawdzenie, czy odpowiedź jest poprawna
    if response.status_code != 200:
        print(f"Failed to fetch data, status code: {response.status_code}")
        return None

    try:
        data = response.json()  # Próba sparsowania JSON
    except ValueError:
        print("Odpowiedź serwera nie jest w formacie JSON")
        return None

    standings = data.get('standings', [])
    all_groups = []

    ratings = get_countries_rating()

    for group in standings:
        group_name = group['tournament']['name']
        for row in group.get('rows', []):
            team_name = row['team']['name']
            points = row['points']
            rating = ratings.get(team_name, 'Brak danych')
            all_groups.append({
                'group': group_name,
                'team': team_name,
                'points': points,
                'rating': rating
            })
    return all_groups

# Funkcja wyświetlająca tabelę wyników
def display_standings():
    teams_info = get_teams_info()
    if teams_info:
        df = pd.DataFrame(teams_info)
        df_sorted = df.sort_values(by=['group'])
        print(df_sorted)
    else:
        print("Nie udało się pobrać danych o zespołach.")

# Funkcja sprawdzająca, czy mecz istnieje już w bazie danych
def match_exists(team1_name, team2_name, team1_goals, team2_goals, cursor):
    cursor.execute('''
        SELECT 1 FROM matches WHERE team1_name = ? AND team2_name = ? 
        AND team1_goals = ? AND team2_goals = ?
    ''', (team1_name, team2_name, team1_goals, team2_goals))
    return cursor.fetchone() is not None

# Funkcja zapisująca mecz do bazy danych
def save_match_to_db(match, cursor, conn):
    if not match_exists(match['team1_name'], match['team2_name'], match.get('team1_goals'), match.get('team2_goals'), cursor):
        cursor.execute('''
            INSERT INTO matches 
            (team1_name, team1_goals, team2_name, team2_goals, team1_penalties, team2_penalties, team1_id, team2_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match['team1_name'],
            match.get('team1_goals'),
            match['team2_name'],
            match.get('team2_goals'),
            match.get('team1_penalties'),
            match.get('team2_penalties'),
            match['team1_id'],
            match['team2_id']
        ))
        conn.commit()

# Funkcja scrapująca wyniki meczów
def scrape_matches_and_save():
    url = "URL_DO_TWOJEJ_STRONY"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table_rows = soup.select("table tbody tr")
        matches = []

        for row in table_rows:
            cells = row.find_all('td')
            if len(cells) >= 8:
                team1_anchor = cells[3].find('a')
                team2_anchor = cells[7].find('a')

                if team1_anchor and team2_anchor:
                    team1_name = unidecode.unidecode(team1_anchor.text.strip())
                    team2_name = unidecode.unidecode(team2_anchor.text.strip())

                    team1_id = team1_anchor['href'].split('/')[-3]
                    team2_id = team2_anchor['href'].split('/')[-3]

                    result_link = cells[5].find('a')
                    result = result_link.text if result_link else 'No Result'
                    match_id = result_link['href'].split('/')[-1] if result_link else 'No Match ID'

                    if "No Result" not in result:
                        result_text = result_link.get_text().strip()

                        if 'po r.k.' in result_text:
                            goals, penalties_info = result_text.split('po r.k.')
                            goals = goals.strip()
                            penalties_info = penalties_info.strip()

                            team1_penalties, team2_penalties = None, None
                            if ':' in goals:
                                penalty_parts = goals.split(':')
                                if len(penalty_parts) == 2 and penalty_parts[0].isdigit() and penalty_parts[1].isdigit():
                                    team1_penalties, team2_penalties = map(int, penalty_parts)

                        else:
                            result_text = result_text.replace('p. d.', '').strip()
                            team1_goals, team2_goals = map(int, result_text.split(':')) if ':' in result_text else (None, None)
                            team1_penalties, team2_penalties = None, None

                        matches.append({
                            "team1_name": team1_name,
                            "team1_goals": team1_goals,
                            "team2_name": team2_name,
                            "team2_goals": team2_goals,
                            "team1_penalties": team1_penalties,
                            "team2_penalties": team2_penalties,
                            "team1_id": team1_id,
                            "team2_id": team2_id
                        })

        # Podłączenie do bazy danych SQLite
        conn = sqlite3.connect('matches.db')
        cursor = conn.cursor()

        for match in matches:
            print(f"{match['team1_name']} ({match['team1_id']}) {match['team1_goals']} : {match['team2_goals']} {match['team2_name']} ({match['team2_id']}) | Penalties: {match['team1_penalties']} : {match['team2_penalties']}")
            save_match_to_db(match, cursor, conn)

        conn.close()
    else:
        print("Failed to retrieve the page")

# Wyświetlanie tabeli
display_standings()
