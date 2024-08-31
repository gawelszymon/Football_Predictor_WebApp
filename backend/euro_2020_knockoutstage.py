import requests
from bs4 import BeautifulSoup
import unidecode
import sqlite3

# Headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# URL of the page to scrape
url = "https://www.transfermarkt.pl/weltmeisterschaft-2006/gesamtspielplan/pokalwettbewerb/WM06/saison_id/2005"

# Send a GET request
response = requests.get(url, headers=headers)

# Database connection and table setup
conn = sqlite3.connect('world_cup_teams_info_2006.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,
        team1 TEXT,
        team1_id TEXT,
        result TEXT,
        team2 TEXT,
        team2_id TEXT,
        team1_stat TEXT,
        team2_stat TEXT
    )
''')


# Function to save match details to the database
def match_exists_and_is_same(match):
    cursor.execute('''
        SELECT team1_stat, team2_stat FROM matches WHERE match_id = ?
    ''', (match['match_id'],))
    row = cursor.fetchone()

    if row:
        existing_team1_stat, existing_team2_stat = row
        return (existing_team1_stat == match['team1_stat'] and existing_team2_stat == match['team2_stat'])
    return False


# Function to save match details to the database
def save_match_to_db(match, team1_stat, team2_stat):
    match['team1_stat'] = team1_stat
    match['team2_stat'] = team2_stat

    if match_exists_and_is_same(match):
        print(f"Match {match['match_id']} already exists with the same data. Skipping update.")
    else:
        cursor.execute('''
            INSERT OR REPLACE INTO matches (match_id, team1, team1_id, result, team2, team2_id, team1_stat, team2_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match['match_id'],
            match['team1'],
            match['team1_id'],
            match['result'],
            match['team2'],
            match['team2_id'],
            match['team1_stat'],
            match['team2_stat']
        ))
        conn.commit()
        print(f"Match {match['match_id']} has been updated in the database.")


if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    table_rows = soup.select("table tbody tr")

    matches = []

    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) >= 6:
            team1_anchor = cells[1].find('a')
            team2_anchor = cells[5].find('a')

            if team1_anchor and team2_anchor:
                team1 = team1_anchor.text.strip()
                team1 = unidecode.unidecode(team1)
                team1_id = team1_anchor['href'].split('/')[-3]

                result_link = cells[3].find('a')
                result = result_link.text if result_link else 'No Result'
                match_id = result_link['href'].split('/')[-1] if result_link else 'No Match ID'

                team2 = team2_anchor.text.strip()
                team2 = unidecode.unidecode(team2)
                team2_id = team2_anchor['href'].split('/')[-3]

                team1_url_part = unidecode.unidecode(team1.replace(' ', '_').lower())
                team2_url_part = unidecode.unidecode(team2.replace(' ', '_').lower())

                if "No Result" not in result:
                    matches.append({
                        "team1": team1,
                        "team1_url_part": team1_url_part,
                        "team1_id": team1_id,
                        "result": result,
                        "team2": team2,
                        "team2_url_part": team2_url_part,
                        "team2_id": team2_id,
                        "match_id": match_id,
                    })

    special_cases = {
        "Irlandia Poln.": "irlandia-polnocna",
        "Korea Pld.": "korea-poludniowa",
        "Arabia Saudy.": "arabia-saudyjska",
        "Macedonia P.": "macedonia-polnocna",
    }

    # Your existing match processing loop
    for match in matches:
        print(
            f"Match ID: {match['match_id']} | {match['team1']} (ID: {match['team1_id']}) {match['result']} {match['team2']} (ID: {match['team2_id']})")

        team1_url_part = special_cases.get(match['team1'], match['team1_url_part'])
        team2_url_part = special_cases.get(match['team2'], match['team2_url_part'])

        match_url = f"https://www.transfermarkt.pl/{team1_url_part}_{team2_url_part}/statistik/spielbericht/{match['match_id']}"

        print(f"Generated Match URL: {match_url}")

        match_response = requests.get(match_url, headers=headers)
        if match_response.status_code == 200:
            match_soup = BeautifulSoup(match_response.content, "html.parser")

            stat_sections = match_soup.find_all("div", class_="sb-statistik")

            team1_stat, team2_stat = "", ""

            for stat_section in stat_sections:
                stat_title = stat_section.find_previous_sibling("div", class_="unterueberschrift").text.strip()

                stat_values = stat_section.find_all("div", class_="sb-statistik-zahl")
                if len(stat_values) >= 2:
                    home_stat = unidecode.unidecode(stat_values[0].text.strip())
                    away_stat = unidecode.unidecode(stat_values[1].text.strip())
                    print(f"{stat_title}: {home_stat} - {away_stat}")

                    team1_stat += f"{stat_title}: {home_stat} | "
                    team2_stat += f"{stat_title}: {away_stat} | "
                else:
                    print(f"{stat_title}: Brak pelnych danych statystycznych.")

            save_match_to_db(match, team1_stat.strip(" | "), team2_stat.strip(" | "))
        else:
            print(f"Failed to retrieve match data for URL: {match_url} | Status Code: {match_response.status_code}")

        print("\n")

    conn.close()