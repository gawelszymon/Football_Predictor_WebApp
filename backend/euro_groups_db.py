import requests
from bs4 import BeautifulSoup
import unidecode
import sqlite3

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

url = "https://www.transfermarkt.pl/weltmeisterschaft-2006/gesamtspielplan/pokalwettbewerb/WM06/saison_id/2005"

response = requests.get(url, headers=headers)

conn = sqlite3.connect('worldcup2006_matches_info.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        team1_id TEXT,
        team1_name TEXT,
        team1_goals INTEGER,
        team2_id TEXT,
        team2_name TEXT,
        team2_goals INTEGER,
        team1_penalties INTEGER,
        team2_penalties INTEGER
    )
''')

def match_exists(team1_name, team2_name, team1_goals, team2_goals):
    cursor.execute('''
        SELECT 1 FROM matches WHERE team1_name = ? AND team2_name = ? 
        AND team1_goals = ? AND team2_goals = ?
    ''', (team1_name, team2_name, team1_goals, team2_goals))
    return cursor.fetchone() is not None

def save_match_to_db(match):
    if not match_exists(match['team1_name'], match['team2_name'], match.get('team1_goals'), match.get('team2_goals')):
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
                team1_name = team1_anchor.text.strip()
                team1_name = unidecode.unidecode(team1_name)

                team2_name = team2_anchor.text.strip()
                team2_name = unidecode.unidecode(team2_name)

                team1_id = team1_anchor['href'].split('/')[-3]
                team2_id = team2_anchor['href'].split('/')[-3]

                result_link = cells[5].find('a')
                result = result_link.text if result_link else 'No Result'
                match_id = result_link['href'].split('/')[-1] if result_link else 'No Match ID'

                if "No Result" not in result:
                    result_link = cells[5].find('a')
                    if result_link:
                        result_text = result_link.get_text().strip()

                        if 'po r.k.' in result_text:
                            goals, penalties_info = result_text.split('po r.k.')
                            goals = goals.strip()
                            penalties_info = penalties_info.strip()

                            team1_goals = team2_goals = None

                            if ':' in goals:
                                penalty_parts = goals.split(':')
                                if len(penalty_parts) == 2 and penalty_parts[0].isdigit() and penalty_parts[
                                    1].isdigit():
                                    team1_penalties, team2_penalties = map(int, penalty_parts)
                                else:
                                    team1_penalties = team2_penalties = None
                            else:
                                team1_penalties = team2_penalties = None

                        else:
                            result_text = result_text.replace('p. d.', '').strip()

                            if ':' in result_text:
                                team1_goals, team2_goals = map(int, result_text.split(':'))
                            else:
                                team1_goals = team2_goals = None

                            team1_penalties = team2_penalties = None

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

    for match in matches:
        print(f"{match['team1_name']} ({match['team1_id']}) {match['team1_goals']} : {match['team2_goals']} {match['team2_name']} ({match['team2_id']}) | Penalties: {match['team1_penalties']} : {match['team2_penalties']}")
        save_match_to_db(match)

    conn.close()
else:
    print("Failed to retrieve the page")