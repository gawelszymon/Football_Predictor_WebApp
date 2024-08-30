import sqlite3
import requests
from bs4 import BeautifulSoup

def create_database(tournament_type, year):
    conn1 = sqlite3.connect(f'{tournament_type}_teams{year}.db')
    cursor1 = conn1.cursor()
    cursor1.execute('''
        CREATE TABLE IF NOT EXISTS players_stats(
            player_id INTEGER PRIMARY KEY,
            goals INTEGER,
            assists INTEGER,
            yellow_cards INTEGER,
            red_cards INTEGER,
            minutes INTEGER,
            squad INTEGER,
            starting_eleven INTEGER,
            substituted_in INTEGER,
            on_bench INTEGER,
            suspended INTEGER,
            injured INTEGER,
            absence INTEGER,
            FOREIGN KEY (player_id) REFERENCES teams (transfermarkt_id),
            FOREIGN KEY (player_id) REFERENCES market_value_history (player_id)
        )
    ''')

    conn1.commit()
    return conn1


def fetch_player_data(player_id, player_name, year):
    if year == 2020:
        url = f"https://www.transfermarkt.com/{player_name}/leistungsdatendetails/spieler/{player_id}/plus/0?saison={year}&verein=&liga=&wettbewerb=&pos=&trainer_id="
    else:
        url = f"https://www.transfermarkt.com/{player_name}/leistungsdatendetails/spieler/{player_id}/plus/0?saison={year-1}&verein=&liga=&wettbewerb=&pos=&trainer_id="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data = {
            "total_goals": 0,
            "total_assists": 0,
            "total_yellow_cards": 0,
            "total_red_cards": 0,
            "minutes_total": 0,
            "Squad": 0,
            "Starting eleven": 0,
            "Substituted in": 0,
            "On the bench": 0,
            "Suspended": 0,
            "Injured": 0,
            "Absence": 0
        }

        box_sections = soup.find_all('div', class_='box')
        num = str(year)[2:]
        for box in box_sections:
            competition_link = box.find('a', {'name': f"EM{num}"})
            if competition_link:
                table = box.find('table')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 7:
                            goals = cols[8].text.strip() if len(cols) > 8 else "0"
                            assists = cols[9].text.strip() if len(cols) > 9 else "0"
                            yellow_cards = cols[10].text.strip() if len(cols) > 10 else "0"
                            second_yellow_cards = cols[11].text.strip() if len(cols) > 11 else "0"
                            red_cards = cols[12].text.strip() if len(cols) > 12 else "0"
                            minutes = cols[13].text.strip() if len(cols) > 13 else "0"

                            if goals != "":
                                data["total_goals"] += int(goals)
                            if assists != "":
                                data["total_assists"] += int(assists)
                            if yellow_cards != "0" and "'" in yellow_cards:
                                data["total_yellow_cards"] += 1
                            if second_yellow_cards != "0" and "'" in second_yellow_cards:
                                data["total_yellow_cards"] += 1
                            if red_cards != "0" and "'" in red_cards:
                                data["total_red_cards"] += 1
                            if minutes != "0":
                                data["minutes_total"] += int(minutes.replace("'", ""))

                    tfoot = table.find('tfoot')
                    if tfoot:
                        td_element = tfoot.find('td')
                        if td_element:
                            text_content = td_element.text.strip()
                            for item in text_content.split(','):
                                key, value = item.split(':')
                                data[key.strip()] = int(value.strip())
                    print(data)
                    return data

    else:
        print(f"Błąd podczas pobierania strony: {response.status_code}")
        return None

def fetch_player_data_world_cup(player_id, player_name, year):
    url = f"https://www.transfermarkt.pl/{player_name}/leistungsdatendetails/spieler/{player_id}/plus/0?saison={year-1}&verein=&liga=&wettbewerb=&pos=&trainer_id="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data = {
            "total_goals": 0,
            "total_assists": 0,
            "total_yellow_cards": 0,
            "total_red_cards": 0,
            "minutes_total": 0,
            "Kadra": 0,
            "Pierwsza jedenastka": 0,
            "Wprowadzenie": 0,
            "Bez występu": 0,
            "Zawieszenie": 0,
            "Kontuzja": 0,
            "Absence": 0
        }

        box_sections = soup.find_all('div', class_='box')
        num = str(year)[2:]
        for box in box_sections:
            competition_link = box.find('a', {'name': f"WM{num}"})
            if competition_link:
                table = box.find('table')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 7:
                            goals = cols[8].text.strip() if len(cols) > 8 else "0"
                            assists = cols[9].text.strip() if len(cols) > 9 else "0"
                            yellow_cards = cols[10].text.strip() if len(cols) > 10 else "0"
                            second_yellow_cards = cols[11].text.strip() if len(cols) > 11 else "0"
                            red_cards = cols[12].text.strip() if len(cols) > 12 else "0"
                            minutes = cols[13].text.strip() if len(cols) > 13 else "0"

                            if goals != "":
                                data["total_goals"] += int(goals)
                            if assists != "":
                                data["total_assists"] += int(assists)
                            if yellow_cards != "0" and "'" in yellow_cards:
                                data["total_yellow_cards"] += 1
                            if second_yellow_cards != "0" and "'" in second_yellow_cards:
                                data["total_yellow_cards"] += 1
                            if red_cards != "0" and "'" in red_cards:
                                data["total_red_cards"] += 1
                            if minutes != "0":
                                data["minutes_total"] += int(minutes.replace("'", ""))

                    tfoot = table.find('tfoot')
                    if tfoot:
                        td_element = tfoot.find('td')
                        if td_element:
                            text_content = td_element.text.strip()
                            for item in text_content.split(','):
                                key, value = item.split(':')
                                data[key.strip()] = int(value.strip())
                    print(data)
                    return data

    else:
        print(f"Błąd podczas pobierania strony: {response.status_code}")
        return None

def save_player_data_to_db(conn, player_id, player_data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO players_stats (
            player_id, goals, assists, yellow_cards, red_cards, minutes, 
            squad, starting_eleven, substituted_in, on_bench, suspended, 
            injured, absence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        player_id,
        player_data.get('total_goals', 0),
        player_data.get('total_assists', 0),
        player_data.get('total_yellow_cards', 0),
        player_data.get('total_red_cards', 0),
        player_data.get('minutes_total', 0),
        player_data.get('Kadra', 0),
        player_data.get('Pierwsza jedenastka', 0),
        player_data.get('Wprowadzenie', 0),
        player_data.get('Bez występu', 0),
        player_data.get('Zawieszenie', 0),
        player_data.get('Kontuzja', 0),
        player_data.get('Absence', 0)
    ))

    conn.commit()

    print(f"Pomyślnie dodano dane dla (ID: {player_id}) do bazy danych.")




def process_teams_data_euro(year):
    conn = sqlite3.connect(f"euro1_teams{year}.db")
    cursor = conn.cursor()

    cursor.execute("SELECT transfermarkt_id, player_name FROM teams")
    players = cursor.fetchall()

    conn1 = create_database('euro1', year)

    for player_id, player_name in players:
        player_stats = fetch_player_data(player_id, player_name, year)
        if player_stats:
            save_player_data_to_db(conn1, player_id, player_stats)

    conn.close()
    conn1.close()

def process_teams_data_wc(year):
    conn = sqlite3.connect(f"world_cup1_teams{year}.db")
    cursor = conn.cursor()

    cursor.execute("SELECT transfermarkt_id, player_name FROM teams")
    players = cursor.fetchall()

    conn1 = create_database('world_cup1', year)

    for player_id, player_name in players:
        player_stats = fetch_player_data_world_cup(player_id, player_name, year)
        if player_stats:
            save_player_data_to_db(conn1, player_id, player_stats)

    conn.close()
    conn1.close()

# fetch_player_data(267160, "adam-buksa")
# fetch_player_data_EM24(937958, "lamine-yamal")
# fetch_player_data_world_cup(8198, "cristiano-ronaldo", 2022)
process_teams_data_wc(2022)

# process_teams_data_euro(2016)
