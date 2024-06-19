import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re
import json

def create_database(tournament_type, year):
    # Utworzenie połączenia z bazą danych SQLite
    conn1 = sqlite3.connect(f'{tournament_type}_teams{year}.db')
    cursor1 = conn1.cursor()

    # Utworzenie tabeli dla drużyn
    cursor1.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team TEXT,
        player_name TEXT,
        transfermarkt_id INTEGER
    )
    ''')

    # Utworzenie tabeli zawodników
    cursor1.execute('''
        CREATE TABLE IF NOT EXISTS players (
            team TEXT,
            player_name TEXT,
            transfermarkt_id INTEGER,
            height INTEGER,
            age INTEGER,
            league TEXT,
            pos CHAR,
            rating FLOAT,
            goals INTEGER, 
            assists INTEGER, 
            matches INTEGER, 
            bigchances INTEGER, 
            keyPasses INTEGER, 
            saves INTEGER, 
            tackleswon INTEGER, 
            successfulDribbles INTEGER, 
            clearances INTEGER
        )
    ''')

    # Utworzenie tabeli dla historii wartości rynkowej
    cursor1.execute('''
    CREATE TABLE IF NOT EXISTS market_value_history (
        player_id INTEGER,
        value REAL,
        date TEXT,
        club TEXT,
        FOREIGN KEY (player_id) REFERENCES teams (transfermarkt_id)
    )
    ''')

    # Zatwierdzenie zmian
    conn1.commit()
    return conn1

def scrap_squad(urll, conn1):
    url = urll
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    teams = []
    tables = soup.find_all("table", {"class": "sortable"})

    for table in tables:
        header = table.find_previous("h3")
        if header:
            team_name = header.find("span", {"class": "mw-headline"}).text
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th")
                cells = row.find_all("td")
                if th and cells:
                    player_name = th.get_text(strip=True)
                    # Przetwarzanie nazwisk zawodników
                    player_name = clean_player_name(player_name)
                    teams.append((team_name, player_name))
                    cursor1 = conn1.cursor()  # Poprawka tutaj
                    cursor1.execute("INSERT INTO teams (team, player_name) VALUES (?, ?)", (team_name, player_name))
                    conn1.commit()

def clean_player_name(player_name):
    if player_name.endswith("(captain)"):
        index = player_name.find("(captain)")
        player_name = player_name[:index]
    if player_name.endswith("(c)"):
        index = player_name.find("(c)")
        player_name = player_name[:index]
    if "(until" in player_name:
        index = player_name.find("(until")
        player_name = player_name[:index]
    if "(from" in player_name:
        index = player_name.find("(from")
        player_name = player_name[:index]
    replacements = {
        "Dani Carvajal": "Daniel Carvajal",
        "Simon Kjær": "Simon Kjaer",
        "Joakim Mæhle": "Joakim Maehle",
        "Đorđe Petrović": "Djordje Petrovic",
        "Srđan Babić": "Srdjan Babic",
        "Srđan Mijailović": "Srdjan Mijailovic",
        "Philipp Mwene": "Phillipp Mwene",
        "Illya Zabarnyi": "Ilya Zabarnyi",
        "İrfan Kahveci": "İrfan Can Kahveci",
        "Saba Lobzhanidze": "Saba Lobjanidze",
        "Igor Diveyev": "Igor Diveev",
        "Vyacheslav Karavayev": "Vyacheslav Karavaev",
        "Andrei Semyonov": "Andrey Semenov",
        "Magomed Ozdoyev": "Magomed Ozdoev",
        "Dmitri Barinov": "Dmitriy Barinov",
        "Yury Dyupin": "Yuriy Dyupin",
        "Fyodor Kudryashov": "Fedor Kudryashov",
        "Georgi Dzhikiya": "Georgiy Dzhikiya",
        "Matvei Safonov": "Matvey Safonov",
        "Yuri Zhirkov": "Yuriy Zhirkov",
        "Aleksei Ionov": "Aleksey Ionov",
        "Daler Kuzyayev": "Daler Kuzyaev",
        "Roman Yevgenyev": "Roman Evgenjev",
        "Carlos Secretário": "Secretário",
        "Eric Lincar": "Erik Lincar",
        "Tomas Gustafsson": "Tomas Antonelius",
        "Goran Đorović": "Goran Djorovic",
        "Miroslav Đukić": "Miroslav Djukic",
        "Albert Nađ": "Albert Nadj",
        "Ole Gunnar Solskjær": "Ole Gunnar Solskjaer",
        "Jesper Grønkjær": "Jesper Grönkjaer",
        "Bjarne Goldbæk": "Bjarne Goldbaek",
        "Peter Kjær": "Peter Kjaer",
        "Frank Lebœuf": "Frank Leboeuf",
        "Antonios Nikopolidis": "Antonis Nikopolidis",
        "Stylianos Venetidis": "Stelios Venetidis",
        "Kostas Chalkias": "Konstantinos Chalkias",
        "Giorgos Karagounis": "Georgios Karagounis",
        "Kostas Katsouranis": "Konstantinos Katsouranis",
        "Sergei Ovchinnikov": "Sergey Ovchinnikov",
        "Dmitri Sychev": "Dmitriy Sychev",
        "Alexey Smertin": "Aleksey Smertin",
        "Andrei Karyaka": "Andrey Karyaka",
        "Dmitri Bulykin": "Dmitriy Bulykin",
        "Dmitri Alenichev": "Dmitriy Alenichev",
        "Dmitri Sennikov": "Dmitriy Sennikov",
        "Dmitri Kirichenko": "Dmitriy Kirichenko",
        "Dmitri Loskov": "Dmitriy Loskov",
        "Aleksei Bugayev": "Aleksey Bugaev",
        "Evgeni Aldonin": "Evgeniy Aldonin",
        "Đovani Roso": "Dovani Roso",
        "Alex Manninger": "Alexander Manninger",
        "Nikos Spiropoulos": "Nikolaos Spyropoulos",
        "Dimitris Salpingidis": "Dimitrios Salpingidis",
        "Sotirios Kyrgiakos": "Sotiris Kyrgiakos",
        "Yannis Goumas": "Giannis Goumas",
        "Nikos Liberopoulos": "Nikolaos Lyberopoulos",
        "Vasili Berezutski": "Vasiliy Berezutskiy",
        "Renat Yanbayev": "Renat Yanbaev",
        "Sergei Ignashevich": "Sergey Ignashevich",
        "Aleksei Berezutski": "Aleksey Berezutskiy",
        "Dmitri Torbinski": "Dmitriy Torbinskiy",
        "Sergei Semak": "Sergey Semak",
        "Daniel Güiza": "Dani Güiza",
        "Johan Wiland": "Johan Sellberg-Wiland",
        "Dmitri Kombarov": "Dmitriy Kombarov",
        "Yevhen Selin": "Yevgen Selin",
        "Oleksandr Aliyev": "Oleksandr Aliev",
        "Fyodor Smolov": "Fedor Smolov",
        "Pavel Mamayev": "Pavel Mamaev",
        "Yuri Lodygin": "Yuriy Lodygin",
        "Guilherme Marinato": "Guilherme",
        "Georgi Shchennikov": "Georgiy Shchennikov",
        "Serhiy Rybalka": "Sergiy Rybalka",
        "Yaroslav Rakitskiy": "Yaroslav Rakitskyi",
        "Hannes Þór Halldórsson": "Hannes Thór Halldórsson",
        "Birkir Már Sævarsson": "Birkir Már Saevarsson",
        "Kolbeinn Sigþórsson": "Kolbeinn Sigthórsson",
        "Jabu Pule": "Jabu Mahlangu",
        "George Koumantarakis": "Georgios Koumantarakis",
        "Yang Pu": "Pu Yang",
        "Wu Chengying": "Chengying Wu",
        "Shao Jiayi": "Jiayi Shao",
        "Sun Jihai": "Jihai Sun",
        "Ma Mingyu": "Mingyu Ma",
        "Hao Haidong": "Haidong Hao",
        "Yu Genwei": "Genwei Yu",
        "Su Maozhen": "Maozhen Su",
        "Gao Yao": "Yao Gao",
        "Li Weifeng": "Weifeng Li",
        "Zhao Junzhe": "Junzhe Zhao",
        "Qu Bo": "Bo Qu",
        "Du Wei": "Wei Du",
        "Li Xiaopeng": "Xiaopeng Li",
        "Qi Hong": "Hong Qi",
        "Xu Yunlong": "Yunlong Xu",
        "Jiang Jin": "Jin Jiang",
        "Ou Chuliang": "Chuliang Ou",
    }
    return replacements.get(player_name, player_name)

def get_transfermarkt_id(player_name):
    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_name.replace(' ', '+')}"
    response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code != 200:
        print(f"Failed to retrieve search results for {player_name}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    player_link = soup.find('a', href=re.compile(r'/profil/spieler/\d+'))
    if player_link:
        profile_url = player_link['href']
        player_id = re.search(r'/profil/spieler/(\d+)', profile_url).group(1)
        return int(player_id)
    else:
        print(f"No player profile link found for {player_name}")
        return None

def add_column_transfermarkt_id(df, conn):
    cursor = conn.cursor()
    for index, row in df.iterrows():
        player_name = row["Player Name"]
        transfermarkt_id = get_transfermarkt_id(player_name)
        if transfermarkt_id:
            cursor.execute("UPDATE teams SET transfermarkt_id = ? WHERE player_name = ?",
                           (transfermarkt_id, player_name))
    conn.commit()

def convert_value(value):
    value = value.replace(',', '.')
    if 'tys' in value:
        value = value.replace('tys. €', '').strip()
        value = float(value) * 1000
    elif 'mln' in value:
        value = value.replace('mln €', '').strip()
        value = float(value) * 1000000
    else:
        value = float(value.replace('€', '').strip())
    return value

def save_market_value_history(player_id, conn):
    url = f"https://www.transfermarkt.pl/ceapi/marketValueDevelopment/graph/{player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.transfermarkt.pl/robert-lewandowski/marktwertverlauf/spieler/{player_id}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            cursor = conn.cursor()
            for item in data['list']:
                market_value = item['mw']
                date_mv = item['datum_mw']
                club = item['verein']
                if market_value == "-":
                    continue
                market_value_converted = convert_value(market_value)
                cursor.execute("INSERT INTO market_value_history (player_id, value, date, club) VALUES (?, ?, ?, ?)",
                               (player_id, market_value_converted, date_mv, club))
            conn.commit()
        except json.JSONDecodeError:
            print("Błąd dekodowania JSON: Odpowiedź nie jest poprawnym JSON.")
            print("Treść odpowiedzi:")
            print(response.text)
        except ValueError as ve:
            print(f"Błąd konwersji wartości: {ve}")
    else:
        print(f"Błąd: Otrzymano status odpowiedzi {response.status_code}")
        print("Treść odpowiedzi:")
        print(response.text)

# tournament = "euro"
# conn = create_database(tournament, 2000)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2000_squads", conn)
# tournament = "euro"
# conn = create_database(tournament, 2004)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2004_squads", conn)
# tournament = "euro"
# conn = create_database(tournament, 2008)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2008_squads", conn)
# tournament = "euro"
# conn = create_database(tournament, 2012)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2012_squads", conn)
# tournament = "euro"
# conn = create_database(tournament, 2016)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2016_squads", conn)
# tournament = "euro"
# conn = create_database(tournament, 2020)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2020_squads", conn)
tournament = "euro"
conn = create_database(tournament, 2024)
# Pobranie danych drużyn
scrap_squad("https://en.wikipedia.org/wiki/UEFA_Euro_2024_squads", conn)
conn.close()

# tournament = "world_cup"
# conn = create_database(tournament, 2002)
# Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/2002_FIFA_World_Cup_squads", conn)
# tournament = "world_cup"
# conn = create_database(tournament, 2006)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/2006_FIFA_World_Cup_squads", conn)
# tournament = "world_cup"
# conn = create_database(tournament, 2010)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/2010_FIFA_World_Cup_squads", conn)
# tournament = "world_cup"
# conn = create_database(tournament, 2014)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/2014_FIFA_World_Cup_squads", conn)
# tournament = "world_cup"
# conn = create_database(tournament, 2018)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/2018_FIFA_World_Cup_squads", conn)
# tournament = "world_cup"
# conn = create_database(tournament, 2022)
# # Pobranie danych drużyn
# scrap_squad("https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_squads", conn)

# Dodanie kolumny Transfermarkt ID
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM teams")
# teams_df = pd.DataFrame(cursor.fetchall(), columns=["Team", "Player Name", "Transfermarkt ID"])
# add_column_transfermarkt_id(teams_df, conn)
#
# # Pobranie historii wartości rynkowej dla każdego zawodnika
# cursor.execute("SELECT DISTINCT transfermarkt_id FROM teams WHERE transfermarkt_id IS NOT NULL")
# player_ids = cursor.fetchall()
# for player_id in player_ids:
#     save_market_value_history(player_id[0], conn)
#
# # Zamknięcie połączenia z bazą danych
# conn.close()
