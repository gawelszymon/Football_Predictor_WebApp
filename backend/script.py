import asyncio
import datetime
import time
import aiohttp
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re

def create_database(tournament_type, year):
    # Utworzenie połączenia z bazą danych SQLite
    conn1 = sqlite3.connect(f'{tournament_type}_teams{year}.db')
    cursor1 = conn1.cursor()

    # Utworzenie tabeli dla drużyn
    cursor1.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER,
        team TEXT,
        player_name TEXT,
        transfermarkt_id INTEGER,
        PRIMARY KEY (team_id, player_name)
    )
    ''')

    # Utworzenie tabeli dla historii wartości rynkowej z dodatkowymi kolumnami na statystyki
    cursor1.execute('''
    CREATE TABLE IF NOT EXISTS market_value_history (
        player_id INTEGER,
        value REAL,
        date TEXT,
        club TEXT,
        club_hash TEXT,
        position TEXT,  -- Nowa kolumna dla pozycji zawodnika
        appearances INTEGER,
        goals INTEGER,
        assists INTEGER,
        yellow_cards INTEGER,
        red_cards INTEGER,
        minutes_played INTEGER,
        clean_sheets INTEGER,  -- Nowa kolumna dla czystych kont (tylko dla bramkarzy)
        conceded_goals INTEGER,  -- Nowa kolumna dla straconych bramek (tylko dla bramkarzy)
        FOREIGN KEY (player_id) REFERENCES teams (transfermarkt_id)
    )
    ''')

    # Zatwierdzenie zmian
    conn1.commit()
    return conn1


def generate_team_id(team_name):
    return abs(hash(team_name))


# Bufor dla przechowywania już pobranych transfermarkt_id
player_id_cache = {}


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def get_transfermarkt_id(session, player_name):
    if player_name in player_id_cache:
        print(f"Using cached ID for {player_name}: {player_id_cache[player_name]}")
        return player_id_cache[player_name]

    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_name.replace(' ', '+')}"
    response_text = await fetch(session, search_url)

    soup = BeautifulSoup(response_text, "html.parser")
    player_link = soup.find('a', href=re.compile(r'/profil/spieler/\d+'))

    if player_link:
        profile_url = player_link['href']
        player_id = re.search(r'/profil/spieler/(\d+)', profile_url).group(1)
        player_id_cache[player_name] = int(player_id)
        return int(player_id)
    else:
        print(f"No player profile link found for {player_name}")
        return None


async def fetch_transfermarkt_ids(session, player_names):
    tasks = [get_transfermarkt_id(session, player_name) for player_name in player_names]
    return await asyncio.gather(*tasks)


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
        "Li Xiaopeng": "Xiaopeng Li",
        "Qi Hong": "Hong Qi",
        "Xu Yunlong": "Yunlong Xu",
        "Jiang Jin": "Jin Jiang",
        "Ou Chuliang": "Chuliang Ou",
        "Lee Woon-jae": "Woon-Jae Lee",
        "Hyun Young-min": "Young-Min Hyun",
        "Choi Sung-yong": "Sung-Yong Choi",
        "Choi Jin-cheul": "Jin-Cheul Choi",
        "Kim Nam-il": "Nam-Il Kim",
        "Yoo Sang-chul": "Sang-Chul Yoo",
        "Kim Tae-young": "Tae-Young Kim",
        "Choi Tae-uk": "Tae-Uk Choi",
        "Seol Ki-hyeon": "Ki-Hyeon Seol",
        "Lee Young-pyo": "Young-Pyo Lee",
        "Choi Yong-soo": "Yong-Soo Choi",
        "Kim Byung-ji": "Byung-Ji Kim",
        "Lee Eul-yong": "Eul-Yong Lee",
        "Lee Chun-soo": "Chun-Soo Lee",
        "Lee Min-sung": "Min-Sung Lee",
        "Cha Du-ri": "Du-Ri Cha",
        "Yoon Jong-hwan": "Jong-Hwan Yoon",
        "Hwang Sun-hong": "Sun-Hong Hwang",
        "Ahn Jung-hwan": "Jung-Hwan Ahn",
        "Hong Myung-bo": "Myung-Bo Hong",
        "Park Ji-sung": "Ji-Sung Park",
        "Song Chong-gug": "Chong-Gug Song",
        "Choi Eun-sung": "Eun-Sung Choi",
        "Patrick M'Boma": "Patrick Mboma",
        "Daniel N'Gom Kome": "Daniel Komé",
        "Valeri Karpin": "Valeriy Karpin",
        "Yegor Titov": "Egor Titov",
        "Dmitri Khokhlov": "Dmitriy Khokhlov",
        "Yu Genwei": "Genwei Yu",
        "Su Maozhen": "Maozhen Su",
        "Gao Yao": "Yao Gao",
        "Li Weifeng": "Weifeng Li",
        "Zhao Junzhe": "Junzhe Zhao",
        "Qu Bo": "Bo Qu",
        "Du Wei": "Wei Du",
        "Eric Djemba-Djemba": "Eric Djemba Djemba",
        "Daniel Ngom Kome": "Daniel Kome",
        "Mohamed Al-Deayea": "Mohammad Al-Deayea",
        "Abdullah Zubromawi": "Abdullah Sulaiman Zubromawi",
        "Ahmed Al-Dokhi": "Ahmad Al-Dokhi",
        "Abdullah Al-Jumaan": "Abdullah Jumaan Al-Dossary",
        "Mohammed Al-Khojali": "Mohammad Khojahali",
        "Mansour Al-Thagafi": "Mansoor Al-Thagafi",
        "Augusto Porozo": "Augusto Poroso",
        "Franky Vandendriessche": "Franky Van Der Elst",
        "Yuri Kovtun": "Yuriy Kovtun",
        "Yuri Nikiforov": "Yuriy Nikiforov",
        "Vyacheslav Dayev": "Vyacheslav Daev",
        "Igor Chugainov": "Igor Chugaynov",
        "Zoubeir Baya": "Zoubaier Baya",
        "Ziad Jaziri": "Zied Jaziri",
        "Imed Mhedhebi": "Imed Mhadhebi",
        "Emir Mkademi": "Amir Mkadmi",
        "Ahmed El-Jaouachi": "Ahmed Jaouachi",
        "Gilles Yapi Yapo": "Gilles Yapi",
        "Predrag Đorđević": "Predrag Djordjevic",
        "Nenad Đorđević": "Nenad Djordjevic",
        "Dušan Petković[29]": "DUnited Statesn Petkovic",
        "Paulo Figueiredo": "Figueiredo",
        "Edson Nobre": "Edson",
        "Amir Hossein Sadeghi": "Amirhossein Sadeghi",
        "Haminu Draman": "Draman Haminu",
        "Alessandro Santos": "Alex",
        "Kim Young-chul": "Young-chul Kim",
        "Kim Jin-kyu": "Jin-kyu Kim",
        "Kim Do-heon": "Do-heon Kim",
        "Park Chu-young": "Chu-young Park",
        "Baek Ji-hoon": "Ji-hoon Baek",
        "Chung Kyung-ho": "Kyung-ho Chung",
        "Kim Sang-sik": "Sang-sik Kim",
        "Cho Jae-jin": "Jae-jin Cho",
        "Kim Yong-dae": "Yong-dae Kim",
        "Kim Young-kwang": "Young-kwang Kim",
        "Cho Won-hee": "Won-hee Cho",
        "Chérif Touré Mamam": "Cheriffe Maman-Touré",
        "Hamad Al-Montashari": "Hamad Al Montashari",
        "Mohammed Ameen": "Mohammad Ameen",
        "Mohammad Massad": "Mohammed Massad",
        "Mohammad Khouja": "Mohammad Khoja",
        "Haykel Guemamdia": "Haykel Gmamdia",
        "Francileudo Santos": "Santos",
        "Jawhar Mnari": "Jaouhar Mnari",
        "Sofiane Melliti": "Sofiene Melliti",
        "Oleh Shelayev": "Oleg Shelayev",
        "Nikos Spyropoulos": "Nikolaos Spyropoulos",
        "Rúben Amorim": "Ruben Amorim",
        "Sakis Prittas": "Athanasios Prittas",
        "Oh Beom-seok": "Beom-seok Oh",
        "Kim Hyung-il": "Hyung-il Kim",
        "Cho Yong-hyung": "Yong-hyung Cho",
        "Kim Bo-kyung": "Bo-kyung Kim",
        "Kim Jung-woo": "Jung-woo Kim",
        "Lee Seung-yeoul": "Seung-yeoul Lee",
        "Kim Jae-sung": "Jae-sung Kim",
        "Lee Jung-soo": "Jeong-soo Lee",
        "Ki Sung-yueng": "Sung-yueng Ki",
        "Lee Chung-yong": "Chung-yong Lee",
        "Jung Sung-ryong": "Sung-ryong Jung",
        "Yeom Ki-hun": "Ki-hun Yeom",
        "Lee Dong-gook": "Dong-gook Lee",
        "Kang Min-soo": "Min-soo Kang",
        "Antar Yahia": "Anthar Yahia",
        "Faouzi Chaouchi": "Fawzi Chaouchi",
        "Michael Dawson[5]": "Michael Dawson",
        "Eugene Galekovic[6]": "Eugene Galekovic",
        "Dragan Mrđa": "Dragan Mrdja",
        "Anđelko Đuričić": "Andjelko Djuricic",
        "Eric Maxim Choupo-Moting": "Eric-Maxim Choupo-Moting",
        "Mohammadou Idrissou": "Mohamadou Idrissou",
        "Guy N'dy Assembé": "Guy Ndy Assembé",
        "Ben Sigmund": "Benjamin Sigmund",
        "Andy Barron": "Andrew Barron",
        "Dave Mulligan": "David Mulligan",
        "Cheick Tioté": "Cheik Tioté",
        "Ri Myong-guk": "Myong-guk Ri",
        "Cha Jong-hyok": "Jong-hyok Cha",
        "Ri Jun-il": "Jun-il Ri",
        "Ri Kwang-chon": "Kwang-chon Ri",
        "Kim Kum-il": "Kum-il Kim",
        "An Chol-hyok": "Chol-hyok An",
        "Ji Yun-nam": "Yun-nam Ji",
        "Jong Tae-se": "Chong Tese",
        "Hong Yong-jo": "Yong-jo Hong",
        "Mun In-guk": "In-guk Mun",
        "Choe Kum-chol": "Kum-Chol Choe",
        "Pak Chol-jin": "Chol-jin Pak",
        "Kim Yong-jun": "Yong-jun Kim",
        "Nam Song-chol": "Song-chol Nam",
        "An Yong-hak": "Yeong-hak Ahn",
        "Kim Myong-gil": "Myong-gil Kim",
        "Ri Chol-myong": "Chol-myong Ri",
        "Kim Myong-won[9]": "Myong-won Kim",
        "Ri Kwang-hyok": "Kwang-hyok Ri",
        "Kim Kyong-il": "Kyong-il Kim",
        "Pak Sung-hyok": "Sung-Hyok Pak",
        "Rúben Amorim[10]": "Rúben Amorim",
        "Jerry Palacios[11]": "Jerry Palacios",
        "Éder Álvarez Balanta": "Éder Balanta",
        "Giorgos Tzavellas": "Georgios Tzavellas",
        "Sayouba Mandé": "Mandé Sayouba",
        "David Myrie[64]": "David Myrie",
        "Rémy Cabella[90]": "Rémy Cabella",
        "Stéphane Ruffier[92]": "Stéphane Ruffier",
        "Morgan Schneiderlin[94]": "Morgan Schneiderlin",
        "Edder Delgado[97]": "Edder Delgado",
        "Kunle Odunlami": "Odunlami Kunle",
        "Emmanuel Agyemang-Badu": "Emmanuel Badu",
        "Adam Larsen Kwarasey": "Adam Kwarasey",
        "Fatau Dauda": "Fatawu Dauda",
        "Cédric Si Mohamed": "Cédric Si Mohammed",
        "Aleksei Kozlov": "Aleksey Kozlov",
        "Viktor Fayzulin": "Viktor Faizulin",
        "Andrey Yeshchenko": "Andrey Eshchenko",
        "Brown Ideye[4]": "Brown Ideye",
        "Kim Chang-soo": "Chang-soo Kim",
        "Yun Suk-young": "Suk-young Yun",
        "Kwak Tae-hwi": "Tae-hwi Kwak",
        "Kim Young-gwon": "Young-gwon Kim",
        "Hwang Seok-ho": "Seok-ho Hwang",
        "Ha Dae-sung": "Dae-sung Ha",
        "Son Heung-min": "Heung-min Son",
        "Lee Keun-ho": "Keun-ho Lee",
        "Koo Ja-cheol": "Ja-cheol Koo",
        "Han Kook-young": "Kook-young Han",
        "Park Jong-woo": "Jong-woo Park",
        "Kim Shin-wook": "Shin-wook Kim",
        "Ji Dong-won": "Dong-won Ji",
        "Hong Jeong-ho": "Jeong-ho Hong",
        "Kim Seung-gyu": "Seung-gyu Kim",
        "Park Joo-ho[159]": "Joo-ho Park",
        "Lee Bum-young": "Bum-young Lee",
        "Ghasem Haddadifar": "Ghasem Hadadifar",
        "Ahmed Elmohamady": "Ahmed El Mohamady",
        "Mohamed Abdel Shafy": "Mohamed Abdelshafi",
        "Yury Gazinsky": "Yuriy Gazinskiy",
        "Aleksandr Yerokhin": "Aleksandr Erokhin",
        "Ali Al-Bulaihi": "Ali Al-Bulayhi",
        "Taisir Al-Jassim": "Taiseer Al-Jassam",
        "Rouzbeh Cheshmi": "Roozbeh Cheshmi",
        "Mbark Boussoufa": "Moubarak Boussoufa",
        "Nikola Kalinić[note 2]": "Nikola Kalinić",
        "Brian Idowu": "Bryan Idowu",
        "Simeon Nwankwo": "Simy",
        "Jung Seung-hyun": "Seung-hyun Jung",
        "Oh Ban-suk": "Ban-suk Oh",
        "Yun Young-sun": "Young-sun Yun",
        "Park Joo-ho": "Joo-ho Park",
        "Ju Se-jong": "Se-jong Ju",
        "Lee Seung-woo": "Seung-woo Lee",
        "Hwang Hee-chan": "Hee-chan Hwang",
        "Kim Min-woo": "Min-woo Kim",
        "Jung Woo-young": "Woo-young Jung",
        "Lee Jae-sung": "Jae-sung Lee",
        "Moon Seon-min": "Seon-min Moon",
        "Jang Hyun-soo": "Hyun-soo Jang",
        "Kim Jin-hyeon": "Jin-hyeon Kim",
        "Go Yo-han": "Yo-han Go",
        "Jo Hyeon-woo": "Hyeon-woo Jo",
        "Ghailene Chaalali": "Ghaylen Chaalali",
        "Kara Mbodji": "Kara Mbodj",
        "Sebas Méndez": "Sebastián Méndez",
        "Hassan Al-Haydos": "Hasan Al-Haydos",
        "MUnited Statesb Kheder": "MUnited Statesb Khoder",
        "Ismaeel Mohammad": "Ismaeel Mohammed",
        "Mostafa Meshaal": "Mustafa Mashaal",
        "Shojae Khalilzadeh": "Shoja Khalilzadeh",
        "Abdulellah Al-Malki": "Abdulelah Al-Malki",
        "Filip Đuričić": "Filip Djuricic",
        "Lawrence Ati-Zigi": "Lawrence Ati Zigi",
         "Yoon Jong-gyu": "Jong-gyu Yoon",
         "Kim Jin-su": "Jin-su Kim",
         "Kim Min-jae": "Min-jae Kim",
         "Hwang In-beom": "In-beom Hwang",
         "Paik Seung-ho": "Seung-ho Paik",
         "Cho Gue-sung": "Gue-sung Cho",
         "Song Bum-keun": "Bum-keun Song",
         "Son Jun-ho": "Jun-ho Son",
         "Na Sang-ho": "Sang-ho Na",
         "Lee Kang-in": "Kang-in Lee",
         "Kwon Kyung-won": "Kyung-won Kwon",
         "Kwon Chang-hoon": "Chang-hoon Kwon",
         "Kim Tae-hwan": "Tae-hwan Kim",
         "Cho Yu-min": "Yu-min Cho",
         "Jeong Woo-yeong": "Woo-yeong Jeong",
         "Song Min-kyu": "Min-kyu Song",
         "Kim Moon-hwan": "Moon-hwan Kim",
         "Munir Mohamedi": "Munir El Kajoui",
         "Musab Kheder": "Musab Khoder",
     }
    return replacements.get(player_name, player_name)


def scrap_squad(url, conn1):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    teams = []
    tables = soup.find_all("table", {"class": "sortable"})

    for table in tables:
        header = table.find_previous("h3")
        if header:
            team_name = header.text.strip()
            if "Player representation" in team_name or "Average age" in team_name or "Coaches representation" in team_name:
                continue  # Pomijamy sekcje, które nie są drużynami
            print(f"Przetwarzanie drużyny: {team_name}")

            # Generowanie team_id
            team_id = generate_team_id(team_name)

            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th")
                cells = row.find_all("td")
                if th and cells:
                    player_name = th.get_text(strip=True)
                    # Przetwarzanie nazwisk zawodników
                    player_name = clean_player_name(player_name)
                    teams.append((team_id, team_name, player_name))
                    cursor1 = conn1.cursor()
                    cursor1.execute("INSERT INTO teams (team_id, team, player_name) VALUES (?, ?, ?)", (team_id, team_name, player_name))
                    conn1.commit()
        else:
            print("Nie znaleziono nagłówka 'h3' przed tabelą.")


def add_column_transfermarkt_id(df, conn):
    cursor = conn.cursor()

    # Zbierz unikalne nazwiska zawodników z dataframe
    player_names = df["Player Name"].unique()

    # Oczyszczanie nazw zawodników przed zapytaniem do transfermarkt
    cleaned_player_names = [clean_player_name(name) for name in player_names]

    # Lista transfermarkt_id do wykluczenia
    excluded_ids = {9811, 132563, 15412, 123951, 327613, 58074, 652782}

    # Asynchroniczne pobieranie transfermarkt_id
    async def main():
        async with aiohttp.ClientSession() as session:
            player_ids = await fetch_transfermarkt_ids(session, cleaned_player_names)
            for player_name, transfermarkt_id in zip(player_names, player_ids):
                if transfermarkt_id:
                    if transfermarkt_id not in excluded_ids:
                        cursor.execute("UPDATE teams SET transfermarkt_id = ? WHERE player_name = ?",
                                       (transfermarkt_id, player_name))
                    else:
                        print(f"Excluding player {player_name} with Transfermarkt ID {transfermarkt_id}")
                else:
                    print(f"Skipping player {player_name} due to missing Transfermarkt ID")
            conn.commit()

    asyncio.run(main())

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

# Map Polish month abbreviations to month numbers
MONTH_MAP = {
    'sty': '01',
    'lut': '02',
    'mar': '03',
    'kwi': '04',
    'maj': '05',
    'cze': '06',
    'lip': '07',
    'sie': '08',
    'wrz': '09',
    'paź': '10',
    'lis': '11',
    'gru': '12'
}

def parse_polish_date(date_str):
    # Replace Polish month abbreviation with corresponding number
    for polish_month, month_number in MONTH_MAP.items():
        if polish_month in date_str:
            date_str = date_str.replace(polish_month, month_number)
            break
    # Convert the date string to datetime object
    return datetime.datetime.strptime(date_str, "%d %m %Y")

def add_club_hash_column_to_market_value_history(conn):
    cursor = conn.cursor()

    # Sprawdzenie, czy kolumna 'club_hash' już istnieje
    cursor.execute("PRAGMA table_info(market_value_history)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'club_hash' not in columns:
        # Jeśli kolumna nie istnieje, dodajemy ją
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN club_hash TEXT
        ''')
        conn.commit()
        print("Kolumna 'club_hash' została dodana do tabeli 'market_value_history'.")
    else:
        print("Kolumna 'club_hash' już istnieje w tabeli 'market_value_history'.")

async def fetch_market_value_history(session, player_id, conn, event_date):
    url = f"https://www.transfermarkt.pl/ceapi/marketValueDevelopment/graph/{player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.transfermarkt.pl/robert-lewandowski/marktwertverlauf/spieler/{player_id}"
    }

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if 'list' in data:
                    # Convert event_date to datetime object
                    event_date = datetime.datetime.strptime(event_date, "%d-%m-%Y")
                    closest_record = None

                    for item in data['list']:
                        market_value = item.get('mw', '-')
                        date_mv = item.get('datum_mw')
                        club = item.get('verein', '')

                        if market_value == "-" or not date_mv or club == "Koniec kariery":
                            continue

                        try:
                            # Convert the date_mv (in "dd mmm yyyy" format) to a datetime object
                            date_mv_obj = parse_polish_date(date_mv)
                        except ValueError:
                            print(f"Invalid date format for player ID {player_id}: {date_mv}")
                            continue

                        if date_mv_obj < event_date:
                            if closest_record is None or date_mv_obj > closest_record['date']:
                                closest_record = {
                                    'player_id': player_id,
                                    'value': market_value,
                                    'date': date_mv_obj,
                                    'club': club,
                                    'club_hash': generate_team_id(club)  # Generate club hash
                                }

                    if closest_record:
                        try:
                            market_value_converted = convert_value(closest_record['value'])
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO market_value_history (player_id, value, date, club, club_hash) 
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                closest_record['player_id'],
                                market_value_converted,
                                closest_record['date'].strftime('%Y-%m-%d'),
                                closest_record['club'],
                                closest_record['club_hash']
                            ))
                            conn.commit()
                            print(f"Inserted record for player ID {player_id}: {market_value_converted} on {closest_record['date'].strftime('%Y-%m-%d')}, club hash: {closest_record['club_hash']}")

                        except ValueError as ve:
                            print(f"Error converting market value '{closest_record['value']}': {ve}")

            else:
                print(f"Failed to retrieve data for player ID {player_id}. Status code: {response.status}")

    except Exception as e:
        print(f"An error occurred while processing player ID {player_id}: {e}")

async def save_market_value_history_async(player_ids, conn, event_date):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_market_value_history(session, player_id, conn, event_date) for player_id in player_ids]
        await asyncio.gather(*tasks)

def save_market_value_history(player_ids, conn, event_date):
    asyncio.run(save_market_value_history_async(player_ids, conn, event_date))







football_teams_info = [
    ("1.FC Köln", "Germany", "UEFA"),
    ("1.FC Union Berlin", "Germany", "UEFA"),
    ("AC Fiorentina", "Italy", "UEFA"),
    ("AC Milan", "Italy", "UEFA"),
    ("AD Guanacasteca", "Costa Rica", "CONCACAF"),
    ("AEK Ateny", "Greece", "UEFA"),
    ("AFC Bournemouth", "England", "UEFA"),
    ("AFC Sunderland", "England", "UEFA"),
    ("AFC Wimbledon", "England", "UEFA"),
    ("AS Monaco", "France", "UEFA"),
    ("AS Roma", "Italy", "UEFA"),
    ("Abha Club", "Saudi Arabia", "AFC"),
    ("Adelaide United", "Australia", "AFC"),
    ("Airbus UK Broughton", "England", "UEFA"),
    ("Ajax Amsterdam", "Netherlands", "UEFA"),
    ("Al-Ahli SC", "Qatar", "AFC"),
    ("Al-Ahli SFC", "Saudi Arabia", "AFC"),
    ("Al-Arabi SC", "Qatar", "AFC"),
    ("Al-Duhail SC", "Qatar", "AFC"),
    ("Al-Ettifaq FC", "Saudi Arabia", "AFC"),
    ("Al-Fateh SC", "Saudi Arabia", "AFC"),
    ("Al-Gharafa SC", "Qatar", "AFC"),
    ("Al-Hilal SFC", "Saudi Arabia", "AFC"),
    ("Al-Ittihad Club", "Saudi Arabia", "AFC"),
    ("Al-Nassr FC", "Saudi Arabia", "AFC"),
    ("Al-Rayyan SC", "Qatar", "AFC"),
    ("Al-Sadd SC", "Qatar", "AFC"),
    ("Al-Shabab FC", "Saudi Arabia", "AFC"),
    ("Al-Wakrah SC", "Qatar", "AFC"),
    ("Al-Wehda FC", "Saudi Arabia", "AFC"),
    ("Alanyaspor", "Türkiye", "UEFA"),
    ("Amiens SC", "France", "UEFA"),
    ("Antalyaspor", "Türkiye", "UEFA"),
    ("Aston Villa", "England", "UEFA"),
    ("Atalanta BC", "Italy", "UEFA"),
    ("Athletic Bilbao", "Spain", "UEFA"),
    ("Atlanta United FC", "United States", "CONCACAF"),
    ("Atlético Madryt", "Spain", "UEFA"),
    ("Atromitos Ateny", "Greece", "UEFA"),
    ("Austin FC", "United States", "CONCACAF"),
    ("Bayer 04 Leverkusen", "Germany", "UEFA"),
    ("Bayern Monachium", "Germany", "UEFA"),
    ("Benevento Calcio", "Italy", "UEFA"),
    ("Benfika Lizbona", "Portugal", "UEFA"),
    ("Besiktas JK", "Türkiye", "UEFA"),
    ("Birmingham City", "England", "UEFA"),
    ("Borussia Dortmund", "Germany", "UEFA"),
    ("Borussia Mönchengladbach", "Germany", "UEFA"),
    ("Brescia Calcio", "Italy", "UEFA"),
    ("Brighton & Hove Albion", "England", "UEFA"),
    ("Bröndby IF", "Denmark", "UEFA"),
    ("CA Newell's Old Boys", "Argentina", "CONMEBOL"),
    ("CA River Plate", "Argentina", "CONMEBOL"),
    ("CD Cruz Azul", "Mexico", "CONCACAF"),
    ("CD Lugo", "Spain", "UEFA"),
    ("CF América", "Mexico", "CONCACAF"),
    ("CF Monterrey", "Mexico", "CONCACAF"),
    ("CF Pachuca", "Mexico", "CONCACAF"),
    ("CS Herediano", "Costa Rica", "CONCACAF"),
    ("CS Sfaxien", "Tunisia", "CAF"),
    ("Carabobo FC", "Venezuela", "CONMEBOL"),
    ("Cardiff City", "England", "UEFA"),
    ("Celta de Vigo", "Spain", "UEFA"),
    ("Celtic Glasgow", "Scotland", "UEFA"),
    ("Central Coast Mariners", "Australia", "AFC"),
    ("Cercle Brügge", "Belgium", "UEFA"),
    ("Charlotte FC", "United States", "CONCACAF"),
    ("Chelsea FC", "England", "UEFA"),
    ("Clermont Foot 63", "France", "UEFA"),
    ("Club Africain Tunis", "Tunisia", "CAF"),
    ("Club León FC", "Mexico", "CONCACAF"),
    ("Columbus Crew", "United States", "CONCACAF"),
    ("Crystal Palace", "England", "UEFA"),
    ("Cádiz CF", "Spain", "UEFA"),
    ("Deportivo Guadalajara", "Mexico", "CONCACAF"),
    ("Deportivo Saprissa", "Costa Rica", "CONCACAF"),
    ("Dundee United FC", "Scotland", "UEFA"),
    ("ESTAC Troyes", "France", "UEFA"),
    ("Eintracht Frankfurt", "Germany", "UEFA"),
    ("El Ahly Kair", "Egypt", "CAF"),
    ("Esperance Tunis", "Tunisia", "CAF"),
    ("Esteghlal FC", "Iran", "AFC"),
    ("Etoile Sportive du Sahel", "Tunisia", "CAF"),
    ("FC Arsenal", "England", "UEFA"),
    ("FC Augsburg", "Germany", "UEFA"),
    ("FC Barcelona", "Spain", "UEFA"),
    ("FC Bologna", "Italy", "UEFA"),
    ("FC Brentford", "England", "UEFA"),
    ("FC Brügge", "Belgium", "UEFA"),
    ("FC Burnley", "England", "UEFA"),
    ("FC Cincinnati", "United States", "CONCACAF"),
    ("FC Dallas", "United States", "CONCACAF"),
    ("FC Everton", "England", "UEFA"),
    ("FC Fulham", "England", "UEFA"),
    ("FC Juárez", "Mexico", "CONCACAF"),
    ("FC Kopenhaga", "Denmark", "UEFA"),
    ("FC Liverpool", "England", "UEFA"),
    ("FC Lorient", "France", "UEFA"),
    ("FC Luzern", "Switzerland", "UEFA"),
    ("FC Middlesbrough", "England", "UEFA"),
    ("FC Paris Saint-Germain", "France", "UEFA"),
    ("FC Porto", "Portugal", "UEFA"),
    ("FC Portsmouth", "England", "UEFA"),
    ("FC Reading", "England", "UEFA"),
    ("FC Sao Paulo", "Brazil", "CONMEBOL"),
    ("FC St. Pauli", "Germany", "UEFA"),
    ("FC Tokyo", "Japan", "AFC"),
    ("FC Watford", "England", "UEFA"),
    ("Fagiano Okayama", "Japan", "AFC"),
    ("Fenerbahce", "Türkiye", "UEFA"),
    ("Ferencvárosi TC", "Hungary", "UEFA"),
    ("Feyenoord Rotterdam", "Netherlands", "UEFA"),
    ("Fortuna Düsseldorf", "Germany", "UEFA"),
    ("GNK Dinamo Zagrzeb", "Croatia", "UEFA"),
    ("Galatasaray", "Türkiye", "UEFA"),
    ("Heart of Midlothian FC", "Scotland", "UEFA"),
    ("Hellas Verona", "Italy", "UEFA"),
    ("Hertha BSC", "Germany", "UEFA"),
    ("Houston Dynamo FC", "United States", "CONCACAF"),
    ("Huddersfield Town", "England", "UEFA"),
    ("Imbabura SC", "Ecuador", "CONMEBOL"),
    ("Independiente del Valle", "Ecuador", "CONMEBOL"),
    ("Inter Mediolan", "Italy", "UEFA"),
    ("Inter Miami CF", "United States", "CONCACAF"),
    ("Juventus Turyn", "Italy", "UEFA"),
    ("KRC Genk", "Belgium", "UEFA"),
    ("Kawasaki Frontale", "Japan", "AFC"),
    ("Kayserispor", "Türkiye", "UEFA"),
    ("Konyaspor", "Türkiye", "UEFA"),
    ("Kuwait SC", "Kuwait", "AFC"),
    ("LD Alajuelense", "Costa Rica", "CONCACAF"),
    ("LDU Quito", "Ecuador", "CONMEBOL"),
    ("LOSC Lille", "France", "UEFA"),
    ("Lech Poznań", "Poland", "UEFA"),
    ("Leeds United", "England", "UEFA"),
    ("Legia Warszawa", "Poland", "UEFA"),
    ("Leicester City", "England", "UEFA"),
    ("Los Angeles FC", "United States", "CONCACAF"),
    ("Luton Town", "England", "UEFA"),
    ("Manchester City", "England", "UEFA"),
    ("Manchester United", "England", "UEFA"),
    ("Millonarios FC", "Colombia", "CONMEBOL"),
    ("Milton Keynes Dons", "England", "UEFA"),
    ("Montpellier HSC", "France", "UEFA"),
    ("Municipal Grecia", "Costa Rica", "CONCACAF"),
    ("Nagoya Grampus", "Japan", "AFC"),
    ("Nashville SC", "United States", "CONCACAF"),
    ("New York City FC", "United States", "CONCACAF"),
    ("New York Red Bulls", "United States", "CONCACAF"),
    ("Newcastle United", "England", "UEFA"),
    ("Norwich City", "England", "UEFA"),
    ("Nottingham Forest", "England", "UEFA"),
    ("OGC Nice", "France", "UEFA"),
    ("Odense Boldklub", "Denmark", "UEFA"),
    ("Olympiakos Pireus", "Greece", "UEFA"),
    ("Olympique Lyon", "France", "UEFA"),
    ("Olympique Marseille", "France", "UEFA"),
    ("Omonia Nikozja", "Cyprus", "UEFA"),
    ("PSV Eindhoven", "Netherlands", "UEFA"),
    ("Pafos FC", "Cyprus", "UEFA"),
    ("Persepolis FC", "Iran", "AFC"),
    ("Pogoń Szczecin", "Poland", "UEFA"),
    ("Queens Park Rangers", "England", "UEFA"),
    ("R Charleroi SC", "Belgium", "UEFA"),
    ("RC Lens", "France", "UEFA"),
    ("RC Strasbourg Alsace", "France", "UEFA"),
    ("RCD Espanyol", "Spain", "UEFA"),
    ("RSC Anderlecht", "Belgium", "UEFA"),
    ("RasenBallsport Leipzig", "Germany", "UEFA"),
    ("Rayo Vallecano", "Spain", "UEFA"),
    ("Real Betis Balompié", "Spain", "UEFA"),
    ("Real Madryt", "Spain", "UEFA"),
    ("Real Salt Lake City", "United States", "CONCACAF"),
    ("Real Valladolid CF", "Spain", "UEFA"),
    ("Royal Antwerpia FC", "Belgium", "UEFA"),
    ("SC Freiburg", "Germany", "UEFA"),
    ("SC Heerenveen", "Netherlands", "UEFA"),
    ("SD Aucas", "Ecuador", "CONMEBOL"),
    ("SD Ponferradina", "Spain", "UEFA"),
    ("SM Caen", "France", "UEFA"),
    ("SSC Napoli", "Italy", "UEFA"),
    ("SV Schalding-Heining", "Germany", "UEFA"),
    ("SV Werder Bremen", "Germany", "UEFA"),
    ("Santos Laguna", "Mexico", "CONCACAF"),
    ("Seattle Sounders FC", "United States", "CONCACAF"),
    ("Sepahan FC", "Iran", "AFC"),
    ("Sevilla FC", "Spain", "UEFA"),
    ("Shabab Al-Ahli Club", "United Arab Emirates", "AFC"),
    ("Sheffield United", "England", "UEFA"),
    ("Shimizu S-Pulse", "Japan", "AFC"),
    ("Spezia Calcio", "Italy", "UEFA"),
    ("St. Mirren FC", "Scotland", "UEFA"),
    ("Stade Reims", "France", "UEFA"),
    ("Stade Rennais FC", "France", "UEFA"),
    ("Stoke City", "England", "UEFA"),
    ("Swansea City", "England", "UEFA"),
    ("Swindon Town", "England", "UEFA"),
    ("Sydney FC", "Australia", "AFC"),
    ("TSG 1899 Hoffenheim", "Germany", "UEFA"),
    ("Tottenham Hotspur", "England", "UEFA"),
    ("Trabzonspor", "Türkiye", "UEFA"),
    ("Tractor Sazi FC", "Iran", "AFC"),
    ("UC Sampdoria", "Italy", "UEFA"),
    ("US Cremonese", "Italy", "UEFA"),
    ("US Monastir", "Tunisia", "CAF"),
    ("US Salernitana 1919", "Italy", "UEFA"),
    ("Urawa Red Diamonds", "Japan", "AFC"),
    ("VV St. Truiden", "Belgium", "UEFA"),
    ("Valencia CF", "Spain", "UEFA"),
    ("Vejle Boldklub", "Denmark", "UEFA"),
    ("VfB Stuttgart", "Germany", "UEFA"),
    ("VfL Wolfsburg", "Germany", "UEFA"),
    ("Villarreal CF", "Spain", "UEFA"),
    ("Vitoria Guimarães SC", "Portugal", "UEFA"),
    ("West Ham United", "England", "UEFA"),
    ("Wolverhampton Wanderers", "England", "UEFA"),
    ("Zamalek SC", "Egypt", "CAF"),
    ("Melbourne City FC", "Australia", "AFC"),
    ("Burgos CF", "Spain", "UEFA"),
    ("FC Southampton", "England", "UEFA"),
    ("CD Leganés", "Spain", "UEFA"),
    ("Real Sociedad", "Spain", "UEFA"),
    ("VfL Bochum", "Germany", "UEFA"),
    ("Shonan Bellmare", "Japan", "AFC"),
    ("FC Schalke 04", "Germany", "UEFA"),
    ("Sporting CP", "Portugal", "UEFA"),
    ("Hatayspor", "Türkiye", "UEFA"),
    ("CF Montréal", "Canada", "CONCACAF"),
    ("KMSK Deinze", "Belgium", "UEFA"),
    ("Vancouver Whitecaps FC", "Canada", "CONCACAF"),
    ("Minnesota United FC", "United States", "CONCACAF"),
    ("Toronto FC", "Canada", "CONCACAF"),
    ("GD Chaves", "Portugal", "UEFA"),
    ("Crvena Zvezda Belgrad", "Serbia", "UEFA"),
    ("FC Basel 1893", "Switzerland", "UEFA"),
    ("Zenit Petersburg", "Russia", "UEFA"),
    ("US Sassuolo", "Italy", "UEFA"),
    ("Panetolikos GFS", "Greece", "UEFA"),
    ("Standard Liège", "Belgium", "UEFA"),
    ("CA Osasuna", "Spain", "UEFA"),
    ("Angers SCO", "France", "UEFA"),
    ("FC Toulouse", "France", "UEFA"),
    ("HNK Hajduk Split", "Croatia", "UEFA"),
    ("Red Bull Salzburg", "Austria", "UEFA"),
    ("St. Johnstone FC", "Scotland", "UEFA"),
    ("Stade Brestois 29", "France", "UEFA"),
    ("Wydad Casablanca", "Morocco", "CAF"),
    ("SSC Bari", "Italy", "UEFA"),
    ("UNAM Pumas", "Mexico", "CONCACAF"),
    ("Qatar SC", "Qatar", "AFC"),
    ("NK Osijek", "Croatia", "UEFA"),
    ("Sociedade Esportiva Palmeiras", "Brazil", "CONMEBOL"),
    ("Glasgow Rangers", "Scotland", "UEFA"),
    ("Coton Sport FC de Garoua", "Cameroon", "CAF"),
    ("Philadelphia Union", "United States", "CONCACAF"),
    ("Hannover 96", "Germany", "UEFA"),
    ("Getafe CF", "Spain", "UEFA"),
    ("BSC Young Boys", "Switzerland", "UEFA"),
    ("Dynamo Moskwa", "Russia", "UEFA"),
    ("KV Mechelen", "Belgium", "UEFA"),
    ("Shanghai Shenhua", "China", "AFC"),
    ("PAOK Saloniki", "Greece", "UEFA"),
    ("Flamengo Rio de Janeiro", "Brazil", "CONMEBOL"),
    ("Torino FC", "Italy", "UEFA"),
    ("UD Almería", "Spain", "UEFA"),
    ("Al-Tai FC", "Saudi Arabia", "AFC"),
    ("1.FSV Mainz 05", "Germany", "UEFA"),
    ("Aris Saloniki", "Greece", "UEFA"),
    ("SC Braga", "Portugal", "UEFA"),
    ("Udinese Calcio", "Italy", "UEFA"),
    ("FC St. Gallen 1879", "Switzerland", "UEFA"),
    ("Hearts of Oak", "Ghana", "CAF"),
    ("Chicago Fire FC", "United States", "CONCACAF"),
    ("KAS Eupen", "Belgium", "UEFA"),
    ("FC Nantes", "France", "UEFA"),
    ("AJ Auxerre", "France", "UEFA"),
    ("KAA Gent", "Belgium", "UEFA"),
    ("Bristol City", "England", "UEFA"),
    ("Lazio Rzym", "Italy", "UEFA"),
    ("FC Seoul", "Korea, South", "AFC"),
    ("Jeonbuk Hyundai Motors", "Korea, South", "AFC"),
    ("Ulsan Hyundai", "Korea, South", "AFC"),
    ("Daegu FC", "Korea, South", "AFC"),
    ("Shandong Taishan", "China", "AFC"),
    ("RCD Mallorca", "Spain", "UEFA"),
    ("FC Lugano", "Switzerland", "UEFA"),
    ("Gamba Osaka", "Japan", "AFC"),
    ("Colombe Sportive du Dja et Lobo", "Cameroon", "CAF"),
    ("CA Vélez Sarsfield", "Argentina", "CONMEBOL"),
    ("Club Nacional", "Uruguay", "CONMEBOL"),
    ("Gimcheon Sangmu", "Korea, South", "AFC"),
    ("CA Independiente", "Argentina", "CONMEBOL"),
    ("Club Athletico Paranaense", "Brazil", "CONMEBOL"),
    ("Orlando City SC", "United States", "CONCACAF"),
    ("Los Angeles Galaxy", "United States", "CONCACAF"),
    ("Asante Kotoko SC", "Ghana", "CAF"),
    ("Daejeon Hana Citizen", "Korea, South", "AFC")
]


def add_columns_to_market_value_history(conn):
    cursor = conn.cursor()

    # Sprawdzenie, czy kolumny już istnieją
    cursor.execute("PRAGMA table_info(market_value_history)")
    columns = [info[1] for info in cursor.fetchall()]

    # Dodajemy kolumny, jeśli nie istnieją
    if 'federation' not in columns:
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN federation TEXT
        ''')

    if 'country' not in columns:
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN country TEXT
        ''')

    if 'ranking' not in columns:
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN ranking INTEGER
        ''')

    conn.commit()
    print("Kolumny 'federation', 'country' i 'ranking' zostały dodane do tabeli 'market_value_history'.")


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def get_ranking(session, federation, country, year):
    urls = {
        "UEFA": f"https://www.transfermarkt.com/uefa-champions-league/nationenwertung/pokalwettbewerb/CL/plus/0?saison_id={year}",
        "CAF": f"https://www.transfermarkt.com/caf-champions-league/nationenwertung/pokalwettbewerb/ACL/plus/0?saison_id={year}",
        "CONMEBOL": f"https://www.transfermarkt.com/copa-libertadores/nationenwertung/pokalwettbewerb/CLI/plus/0?saison_id={year}",
        "CONCACAF": f"https://www.transfermarkt.com/concacaf-champions-cup/nationenwertung/pokalwettbewerb/CCL/plus/0?saison_id={year}",
        "AFC": f"https://www.transfermarkt.com/afc-champions-league/nationenwertung/pokalwettbewerb/AFCL/plus/0?saison_id={year}",
        "OFC": f"https://www.transfermarkt.com/ofc-champions-league/nationenwertung/pokalwettbewerb/OCL/plus/0?saison_id={year}",
        "UEFA_EL": f"https://www.transfermarkt.com/uefa-europa-league/nationenwertung/pokalwettbewerb/EL/plus/0?saison_id={year}",
        "CONMEBOL_CS": f"https://www.transfermarkt.com/copa-sudamericana/nationenwertung/pokalwettbewerb/CS/plus/0?saison_id={year}",
    }

    if federation not in urls:
        print(f"Nieznana federacja: {federation}")
        return None

    url = urls[federation]
    ranking = 0

    try:
        response_text = await fetch(session, url)

        soup = BeautifulSoup(response_text, 'html.parser')
        rows = soup.find_all('tr', {'class': ['odd', 'even']})
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 1 and country.lower() in cells[1].text.lower():
                rank = int(cells[0].text.strip())
                adjusted_ranking = 100 - (rank - 1) * 2
                ranking += adjusted_ranking
                break

        # Dodanie dodatkowego rankingu z Europa League dla UEFA
        if federation == "UEFA":
            europa_league_url = urls.get("UEFA_EL")
            if europa_league_url:
                response_text = await fetch(session, europa_league_url)
                soup = BeautifulSoup(response_text, 'html.parser')
                rows = soup.find_all('tr', {'class': ['odd', 'even']})
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1 and country.lower() in cells[1].text.lower():
                        rank = int(cells[0].text.strip())
                        additional_ranking = (100 - (rank - 1) * 2) / 4  # Dodanie połowy wartości
                        ranking += additional_ranking
                        break

        if federation == "CONMEBOL":
            sudamericana_url = urls.get("CONMEBOL_CS")
            if sudamericana_url:
                response_text = await fetch(session, sudamericana_url)
                soup = BeautifulSoup(response_text, 'html.parser')
                rows = soup.find_all('tr', {'class': ['odd', 'even']})
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1 and country.lower() in cells[1].text.lower():
                        rank = int(cells[0].text.strip())
                        additional_ranking = (100 - (rank - 1) * 2) / 4  # Dodanie połowy wartości
                        ranking += additional_ranking
                        break

    except Exception as e:
        print(f"Error fetching the URL {url}: {str(e)}")

    return ranking if ranking > 0 else None


async def update_market_value_history_with_rankings(conn, football_teams_info, year):
    cursor = conn.cursor()

    # Dodanie kolumny dla federacji, kraju i rankingu, jeśli nie istnieją
    cursor.execute("PRAGMA table_info(market_value_history)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'federation' not in columns:
        cursor.execute("ALTER TABLE market_value_history ADD COLUMN federation TEXT")
    if 'country' not in columns:
        cursor.execute("ALTER TABLE market_value_history ADD COLUMN country TEXT")
    if 'ranking' not in columns:
        cursor.execute("ALTER TABLE market_value_history ADD COLUMN ranking INTEGER")
    conn.commit()

    cursor.execute("SELECT DISTINCT club FROM market_value_history")
    clubs = cursor.fetchall()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for (club,) in clubs:
            # Znajdź kraj i federację dla klubu
            team_info = next((info for info in football_teams_info if info[0] == club), None)

            if team_info:
                country = team_info[1]
                federation = team_info[2]

                tasks.append(get_ranking(session, federation, country, year))

        rankings = await asyncio.gather(*tasks)

        for (club,), ranking in zip(clubs, rankings):
            team_info = next((info for info in football_teams_info if info[0] == club), None)
            if team_info:
                country = team_info[1]
                federation = team_info[2]

                # Aktualizacja tabeli market_value_history
                cursor.execute('''
                    UPDATE market_value_history 
                    SET federation = ?, country = ?, ranking = ?
                    WHERE club = ?
                ''', (federation, country, int(ranking) if ranking is not None else 10, club))

    conn.commit()


def add_columns_for_goalkeepers(conn):
    cursor = conn.cursor()

    # Sprawdzenie, czy kolumny dla bramkarzy już istnieją
    cursor.execute("PRAGMA table_info(market_value_history)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'clean_sheets' not in columns:
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN clean_sheets INTEGER
        ''')

    if 'conceded_goals' not in columns:
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN conceded_goals INTEGER
        ''')

    conn.commit()
    print("Kolumny 'clean_sheets' i 'conceded_goals' zostały dodane do tabeli 'market_value_history'.")


async def fetch_player_stats(session, player_id, year):
    url = f"https://www.transfermarkt.com/robert-lewandowski/leistungsdatendetails/spieler/{player_id}/plus/0?saison={year}&verein=&liga=&wettbewerb=&pos=&trainer_id="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.transfermarkt.com/robert-lewandowski/leistungsdatendetails/spieler/{player_id}/"
    }

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.text()
                soup = BeautifulSoup(data, 'html.parser')

                # Pobieranie pozycji zawodnika
                position_element = soup.select_one("#tm-main > header > div.data-header__info-box > div > ul:nth-child(2) > li:nth-child(2) > span")
                position = position_element.text.strip() if position_element else "Unknown"

                # Sprawdzenie, czy zawodnik jest bramkarzem
                is_goalkeeper = "Goalkeeper" in position

                tfoot = soup.find('tfoot')
                if tfoot:
                    stats_table = tfoot.find_all('td')
                    print(f"Debug: stats_table for player {player_id} - {stats_table}")
                    print(f"Debug: stats_table length for player {player_id} - {len(stats_table)}")

                    if is_goalkeeper:
                        # Statystyki dla bramkarzy
                        appearances = stats_table[3].text.strip() or '0'
                        yellow_red_cards = stats_table[5].text.strip().split('/')
                        yellow_cards = yellow_red_cards[0].strip() or '0'
                        red_cards = yellow_red_cards[2].strip() or '0'
                        conceded_goals = stats_table[6].text.strip() or '0'
                        clean_sheets = stats_table[7].text.strip() or '0'
                        minutes_played = stats_table[8].text.strip().replace(".", "").replace("'", "") or '0'

                        stats = {
                            "appearances": appearances,
                            "clean_sheets": clean_sheets,  # Czyste konta
                            "conceded_goals": conceded_goals,  # Stracone bramki
                            "yellow_cards": yellow_cards,
                            "red_cards": red_cards,
                            "minutes_played": minutes_played,
                            "position": position
                        }
                    else:
                        # Statystyki dla zawodników z pola
                        stats = {
                            "appearances": stats_table[3].text.strip() or '0',
                            "goals": stats_table[4].text.strip() or '0',
                            "assists": stats_table[5].text.strip() or '0',
                            "yellow_cards": stats_table[6].text.strip().split("/")[0].strip() or '0',
                            "red_cards": stats_table[6].text.strip().split("/")[1].strip() or '0',
                            "minutes_played": stats_table[7].text.strip().replace("'", "") or '0',
                            "position": position
                        }

                    print(f"Debug: Parsed stats for player {player_id} - {stats}")
                    return stats
                else:
                    print(f"No stats found in tfoot for player ID {player_id}.")
                    return None
            else:
                print(f"Failed to retrieve data for player ID {player_id}. Status code: {response.status}")
                return None
    except Exception as e:
        print(f"An error occurred while processing player ID {player_id}: {e}")
        return None


async def save_player_stats_async(player_ids, year, conn):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_player_stats(session, player_id, year) for player_id in player_ids]
        player_stats = await asyncio.gather(*tasks)

        cursor = conn.cursor()
        for player_id, stats in zip(player_ids, player_stats):
            if stats:
                try:
                    if stats["position"] == "Goalkeeper":
                        cursor.execute('''
                            UPDATE market_value_history 
                            SET appearances = ?, clean_sheets = ?, conceded_goals = ?, yellow_cards = ?, red_cards = ?, minutes_played = ?, position = ?
                            WHERE player_id = ?
                        ''', (
                            stats["appearances"],
                            stats["clean_sheets"],
                            stats["conceded_goals"],
                            stats["yellow_cards"],
                            stats["red_cards"],
                            stats["minutes_played"],
                            stats["position"],
                            player_id
                        ))
                    else:
                        cursor.execute('''
                            UPDATE market_value_history 
                            SET appearances = ?, goals = ?, assists = ?, yellow_cards = ?, red_cards = ?, minutes_played = ?, position = ?
                            WHERE player_id = ?
                        ''', (
                            stats["appearances"],
                            stats["goals"],
                            stats["assists"],
                            stats["yellow_cards"],
                            stats["red_cards"],
                            stats["minutes_played"],
                            stats["position"],
                            player_id
                        ))
                    print(f"Inserted stats for player ID {player_id} into the database.")
                except Exception as e:
                    print(f"Failed to insert stats for player ID {player_id}: {e}")
        conn.commit()



def save_player_stats(player_ids, year, conn):
    asyncio.run(save_player_stats_async(player_ids, year, conn))


# Call this function in your scraping process
def run_scraping_process(year, tournament):
    try:
        tournament = tournament
        year = year - 1
        conn = create_database(tournament, year+1)
        print("Baza danych została utworzona.")

        # Dodanie kolumny hashy klubów (jeśli nie została wcześniej dodana)
        add_club_hash_column_to_market_value_history(conn)
        print("Kolumna hashów klubów została dodana (jeśli nie istniała).")

        # Pobranie danych drużyn
        scrap_squad("https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_squads", conn)
        print("Dane drużyn zostały pobrane i zapisane do bazy danych.")

        # Pobieranie listy drużyn i zawodników z bazy danych
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams")
        teams_df = pd.DataFrame(cursor.fetchall(), columns=["Team ID", "Team", "Player Name", "Transfermarkt ID"])

        # Dodanie kolumny Transfermarkt ID
        add_column_transfermarkt_id(teams_df, conn)
        print("Kolumna Transfermarkt ID została dodana i zaktualizowana.")

        # Pobieranie historii wartości rynkowej dla każdego zawodnika
        cursor.execute("SELECT DISTINCT transfermarkt_id FROM teams WHERE transfermarkt_id IS NOT NULL")
        player_ids = cursor.fetchall()

        # player_ids is a list of tuples, convert it to a flat list
        player_ids = [pid[0] for pid in player_ids]

        # Call the function with the list of player IDs
        save_market_value_history(player_ids, conn, "20-11-2022")
        print("Historia wartości rynkowej została pobrana i zapisana.")

        # Dodajemy informacje o federacji, kraju i rankingu do market_value_history
        asyncio.run(update_market_value_history_with_rankings(conn, football_teams_info, year))
        print("Informacje o federacji, kraju i rankingu zostały zaktualizowane.")

        # Pobieranie i zapisywanie statystyk zawodników
        save_player_stats(player_ids, year, conn)
        print("Statystyki zawodników zostały pobrane i zapisane.")

        # Zamknięcie połączenia z bazą danych
        conn.close()
        print("Połączenie z bazą danych zostało zamknięte.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

# Wywołanie funkcji głównej, aby uruchomić cały proces dla konkretnego roku
run_scraping_process(2022, "world_cup1")

