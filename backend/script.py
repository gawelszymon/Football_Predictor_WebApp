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
    if player_name == "Jô":
        return 34156
    if player_name == "Pak Nam-chol II":
        return 114610
    if player_name == "Pak Nam-chol I":
        return 68565
    if player_name == "Ki Sung-yueng":
        return 81796
    if player_name == "DUnited Statesn Petkovic":
        return 997774
    if player_name == "Hamad Al Montashari":
        return 31662
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
        "Vince Grella": "Vincenzo Grella",
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
                    cursor1.execute("INSERT INTO teams (team_id, team, player_name) VALUES (?, ?, ?)",
                                    (team_id, team_name, player_name))
                    conn1.commit()
        else:
            print("Nie znaleziono nagłówka 'h3' przed tabelą.")


def add_column_transfermarkt_id(df, conn):
    cursor = conn.cursor()

    # Zbierz unikalne nazwiska zawodników z dataframe
    player_names = df["Player Name"].unique()

    # Oczyszczanie nazw zawodników przed zapytaniem do transfermarkt
    cleaned_player_names = [clean_player_name(name) for name in player_names]

    # Asynchroniczne pobieranie transfermarkt_id
    async def main():
        async with aiohttp.ClientSession() as session:
            player_ids = await fetch_transfermarkt_ids(session, cleaned_player_names)
            for player_name, transfermarkt_id in zip(player_names, player_ids):
                if transfermarkt_id:
                    cursor.execute("UPDATE teams SET transfermarkt_id = ? WHERE player_name = ?",
                                    (transfermarkt_id, player_name))
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
                                    'club': club
                                }

                    if closest_record:
                        try:
                            market_value_converted = convert_value(closest_record['value'])
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO market_value_history (player_id, value, date, club) 
                                VALUES (?, ?, ?, ?)
                            """, (
                                closest_record['player_id'],
                                market_value_converted,
                                closest_record['date'].strftime('%Y-%m-%d'),
                                closest_record['club']
                            ))
                            conn.commit()
                            print(
                                f"Inserted record for player ID {player_id}: {market_value_converted} on {closest_record['date'].strftime('%Y-%m-%d')}")

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
    ("Daejeon Hana Citizen", "Korea, South", "AFC"),
    ("Rubin Kazań", "Russia", "UEFA"),
    ("Spartak Moskwa", "Russia", "UEFA"),
    ("Lokomotiw Moskwa", "Russia", "UEFA"),
    ("Al-Taawoun FC", "Saudi Arabia", "AFC"),
    ("CSKA Moskwa", "Russia", "UEFA"),
    ("Masr El Makasa", "Egypt", "CAF"),
    ("Akhmat Grozny", "Russia", "UEFA"),
    ("Wigan Athletic", "England", "UEFA"),
    ("CA Peñarol", "Uruguay", "CONMEBOL"),
    ("West Bromwich Albion", "England", "UEFA"),
    ("Cruzeiro Belo Horizonte", "Brazil", "CONMEBOL"),
    ("Genoa CFC", "Italy", "UEFA"),
    ("Girona FC", "Spain", "UEFA"),
    ("Arsenal Tula", "Russia", "UEFA"),
    ("Saipa FC", "Iran", "AFC"),
    ("Zob Ahan Esfahan", "Iran", "AFC"),
    ("Östersunds FK", "Sweden", "UEFA"),
    ("FK Krasnodar", "Russia", "UEFA"),
    ("Amkar Perm", "Russia", "UEFA"),
    ("Al-Raed SFC", "Saudi Arabia", "AFC"),
    ("CA Boca Juniors", "Argentina", "CONMEBOL"),
    ("CS Marítimo", "Portugal", "UEFA"),
    ("Levante UD", "Spain", "UEFA"),
    ("Renaissance de Berkane", "Morocco", "CAF"),
    ("Al-Jazira Club", "United Arab Emirates", "AFC"),
    ("Ittihad Tanger", "Morocco", "CAF"),
    ("Padideh Khorasan FC", "Iran", "AFC"),
    ("Málaga CF", "Spain", "UEFA"),
    ("AZ Alkmaar", "Netherlands", "UEFA"),
    ("Basaksehir FK", "Turkey", "UEFA"),
    ("Suwon Samsung Bluewings", "South Korea", "AFC"),
    ("FC Millwall", "England", "UEFA"),
    ("Yokohama F. Marinos", "Japan", "AFC"),
    ("Grasshopper Club Zurych", "Switzerland", "UEFA"),
    ("Hull City", "England", "UEFA"),
    ("Newcastle United Jets", "Australia", "AFC"),
    ("Yeni Malatyaspor", "Turkey", "UEFA"),
    ("Puebla FC", "Mexico", "CONCACAF"),
    ("Monarcas Morelia", "Mexico", "CONCACAF"),
    ("Universitario de Deportes", "Peru", "CONMEBOL"),
    ("Portland Timbers", "United States", "CONCACAF"),
    ("Aalborg BK", "Denmark", "UEFA"),
    ("Tiburones Rojos de Veracruz", "Mexico", "CONCACAF"),
    ("Lobos BUAP (- 2019)", "Mexico", "CONCACAF"),
    ("Tigres UANL", "Mexico", "CONCACAF"),
    ("Universidad Técnica de Cajamarca", "Peru", "CONMEBOL"),
    ("Ipswich Town", "England", "UEFA"),
    ("Club Alianza Lima", "Peru", "CONMEBOL"),
    ("Hebei China Fortune", "China", "AFC"),
    ("Hibernian FC", "Scotland", "UEFA"),
    ("FBC Melgar", "Peru", "CONMEBOL"),
    ("Bursaspor", "Turkey", "UEFA"),
    ("FC Girondins Bordeaux", "France", "UEFA"),
    ("Deportivo de La Coruña", "Spain", "UEFA"),
    ("FK Rostov", "Russia", "UEFA"),
    ("Hammarby IF", "Sweden", "UEFA"),
    ("KV Oostende (-2024)", "Belgium", "UEFA"),
    ("FC Roskilde", "Denmark", "UEFA"),
    ("Dalian Yifang", "China", "AFC"),
    ("HNK Rijeka", "Croatia", "UEFA"),
    ("Randers FC", "Denmark", "UEFA"),
    ("Göztepe", "Turkey", "UEFA"),
    ("UD Las Palmas", "Spain", "UEFA"),
    ("KSC Lokeren (- 2020)", "Belgium", "UEFA"),
    ("Dynamo Kijów", "Ukraine", "UEFA"),
    ("Tianjin Teda", "China", "AFC"),
    ("FC Augsburg", "Germany", "UEFA"),
    ("Udinese Calcio", "Italy", "UEFA"),
    ("1.FSV Mainz 05", "Germany", "UEFA"),
    ("Changchun Yatai", "China", "AFC"),
    ("RC Deportivo Fabril", "Spain", "UEFA"),
    ("Grêmio Porto Alegre", "Brazil", "CONMEBOL"),
    ("ADO Den Haag", "Netherlands", "UEFA"),
    ("Levski Sofia", "Bulgaria", "UEFA"),
    ("Kardemir Karabükspor", "Turkey", "UEFA"),
    ("FC Sao Paulo", "Brazil", "CONMEBOL"),
    ("FC Crotone", "Italy", "UEFA"),
    ("Chippa United", "South Africa", "CAF"),
    ("SV Werder Bremen", "Germany", "UEFA"),
    ("Santos de Guápiles FC", "Costa Rica", "CONCACAF"),
    ("FC Nantes", "France", "UEFA"),
    ("Kasimpasa", "Turkey", "UEFA"),
    ("SK Rapid Wiedeń", "Austria", "UEFA"),
    ("Rionegro Águilas", "Colombia", "CONMEBOL"),
    ("FC Reading", "England", "UEFA"),
    ("Sport Club Corinthians Paulista", "Brazil", "CONMEBOL"),
    ("Vitoria Guimarães SC", "Portugal", "UEFA"),
    ("Hapoel Beer Sheva", "Israel", "UEFA"),
    ("AFC Sunderland", "England", "UEFA"),
    ("Deportivo Municipal", "Peru", "CONMEBOL"),
    ("Deportivo Saprissa", "Costa Rica", "CONCACAF"),
    ("FC Kopenhaga", "Denmark", "UEFA"),
    ("RCD Espanyol", "Spain", "UEFA"),
    ("FC Lausanne-Sport", "Switzerland", "UEFA"),
    ("Beijing Guoan", "China", "AFC"),
    ("Minnesota United FC", "United States", "CONCACAF"),
    ("Vancouver Whitecaps FC", "Canada", "CONCACAF"),
    ("LD Alajuelense", "Costa Rica", "CONCACAF"),
    ("FK Partizan Belgrad", "Serbia", "UEFA"),
    ("Hamburger SV", "Germany", "UEFA"),
    ("PAOK Saloniki", "Greece", "UEFA"),
    ("FC Everton", "England", "UEFA"),
    ("RSC Anderlecht", "Belgium", "UEFA"),
    ("Trabzonspor", "Turkey", "UEFA"),
    ("Cercle Brügge", "Belgium", "UEFA"),
    ("Newcastle United", "England", "UEFA"),
    ("KRC Genk", "Belgium", "UEFA"),
    ("Maccabi Tel Aviv", "Israel", "UEFA"),
    ("Crystal Palace", "England", "UEFA"),
    ("CA Boca Juniors", "Argentina", "CONMEBOL"),
    ("Crvena Zvezda Belgrad", "Serbia", "UEFA"),
    ("SD Eibar", "Spain", "UEFA"),
    ("Aberdeen FC", "Scotland", "UEFA"),
    ("SV Sandhausen", "Germany", "UEFA"),
    ("Eintracht Frankfurt", "Germany", "UEFA"),
    ("Western Sydney Wanderers", "Australia", "AFC"),
    ("Antalyaspor", "Turkey", "UEFA"),
    ("1.FC Köln", "Germany", "UEFA"),
    ("FC Toulouse", "France", "UEFA"),
    ("Brighton & Hove Albion", "England", "UEFA"),
    ("New York City FC", "United States", "CONCACAF"),
    ("Los Angeles Galaxy", "United States", "CONCACAF"),
    ("CF Pachuca", "Mexico", "CONCACAF"),
    ("RC Deportivo Fabril", "Spain", "UEFA"),
    ("VfL Wolfsburg", "Germany", "UEFA"),
    ("KVRS Waasland - SK Beveren", "Belgium", "UEFA"),
    ("Al-Ain FC", "United Arab Emirates", "AFC"),
    ("Atlético Bucaramanga", "Colombia", "CONMEBOL"),
    ("Huachipato FC", "Chile", "CONMEBOL"),
    ("San Jose Earthquakes", "United States", "CONCACAF"),
    ("CD Plaza Amador", "Panama", "CONCACAF"),
    ("FC Dinamo 1948", "Romania", "UEFA"),
    ("Boavista Porto FC", "Portugal", "UEFA"),
    ("Kasimpasa", "Turkey", "UEFA"),
    ("Esperance Tunis", "Tunisia", "CAF"),
    ("Etoile Sportive du Sahel", "Tunisia", "CAF"),
    ("CS Sfaxien", "Tunisia", "CAF"),
    ("Cafetaleros de Tapachula", "Mexico", "CONCACAF"),
    ("OGC Nice", "France", "UEFA"),
    ("Sociedade Esportiva Palmeiras", "Brazil", "CONMEBOL"),
    ("Club Africain Tunis", "Tunisia", "CAF"),
    ("KAA Gent U21", "Belgium", "UEFA"),
    ("Deportivo Cali", "Colombia", "CONMEBOL"),
    ("Vissel Kobe", "Japan", "AFC"),
    ("Montpellier HSC", "France", "UEFA"),
    ("Sagan Tosu", "Japan", "AFC"),
    ("Once Caldas", "Colombia", "CONMEBOL"),
    ("Al-Ettifaq FC", "Saudi Arabia", "AFC"),
    ("Olimpia Asunción", "Paraguay", "CONMEBOL"),
    ("Deportivo Alavés", "Spain", "UEFA"),
    ("Kashima Antlers", "Japan", "AFC"),
    ("CSD Municipal", "Guatemala", "CONCACAF"),
    ("Deportes Tolima", "Colombia", "CONMEBOL"),
    ("Jeonbuk Hyundai Motors", "South Korea", "AFC"),
    ("Gamba Osaka", "Japan", "AFC"),
    ("Hamburger SV", "Germany", "UEFA"),
    ("Ludogorets Razgrad", "Bulgaria", "UEFA"),
    ("FC Metz", "France", "UEFA"),
    ("Kashiwa Reysol", "Japan", "AFC"),
    ("DAC Dunajska Streda", "Slovakia", "UEFA"),
    ("Houston Dynamo", "United States", "CONCACAF"),
    ("Stade Rennais FC", "France", "UEFA"),
    ("Dijon FCO", "France", "UEFA"),
    ("Al-Batin FC", "Saudi Arabia", "AFC"),
    ("Górnik Zabrze", "Poland", "UEFA"),
    ("SPAL 2013", "Italy", "UEFA"),
    ("Horoya AC", "Guinea", "CAF"),
    ("Birmingham City", "England", "UEFA"),
    ("FC Girondins Bordeaux", "France", "UEFA"),
    ("Hellas Verona", "Italy", "UEFA"),
    ("Fortuna Düsseldorf", "Germany", "UEFA"),
    ("CD Numancia", "Spain", "UEFA"),
    ("Bez klubu", "Unknown", "Unknown"),
    ("CA Talleres", "Argentina", "CONMEBOL"),
    ("Vålerenga Fotball Elite", "Norway", "UEFA"),
    ("FC Nordsjaelland", "Denmark", "UEFA"),
    ("Enyimba Aba", "Nigeria", "CAF"),
    ("Szachtar Donieck", "Ukraine", "UEFA"),
    ("Deportivo Toluca", "Mexico", "CONCACAF"),
    ("Sangju Sangmu", "South Korea", "AFC"),
    ("Incheon United", "South Korea", "AFC"),
    ("EA Guingamp", "France", "UEFA"),
    ("Cerezo Osaka", "Japan", "AFC"),
    ("Atlas Guadalajara", "Mexico", "CONCACAF"),
    ("Club Universidad de Chile", "Chile", "CONMEBOL"),
    ("Jeju United", "South Korea", "AFC"),
    ("LB Châteauroux", "France", "UEFA"),
    ("KAS Eupen", "Belgium", "UEFA"),
    ("Horoya AC", "Guinea", "CAF"),
    ("Santos de Guápiles FC", "Costa Rica", "CONCACAF"),
    ("Alanyaspor", "Turkey", "UEFA"),
    ("Birmingham City", "England", "UEFA"),
    ("Etoile Sportive du Sahel", "Tunisia", "CAF"),
    ("Hannover 96", "Germany", "UEFA"),
    ("Górnik Zabrze", "Poland", "UEFA"),
    ("Guangzhou Evergrande Taobao", "China", "AFC"),
    ("OGC Nice", "France", "UEFA"),
    ("SK Rapid Wiedeń", "Austria", "UEFA"),
    ("Legia Warszawa", "Poland", "UEFA"),
    ("Tianjin Quanjian", "China", "AFC"),
    ("Kawasaki Frontale", "Japan", "AFC"),
    ("Sociedade Esportiva Palmeiras", "Brazil", "CONMEBOL"),
    ("SPAL 2013", "Italy", "UEFA"),
    ("Amiens SC", "France", "UEFA"),
    ("Fortuna Düsseldorf", "Germany", "UEFA"),
    ("Lechia Gdańsk", "Poland", "UEFA"),
    ("Europa FC", "Gibraltar", "UEFA"),
    ("Nieznany", "Brak", "Brak"),
    ("FSV Frankfurt", "Germany", "UEFA"),
    ("Lokomotiv Moskau", "Russia", "UEFA"),
    ("Preston North End", "England", "UEFA"),
    ("FC Sion", "Switzerland", "UEFA"),
    ("Malmö FF", "Sweden", "UEFA"),
    ("NK Lokomotiva Zagreb", "Croatia", "UEFA"),
    ("CD Universidad Católica", "Chile", "CONMEBOL"),
    ("Heracles Almelo", "Netherlands", "UEFA"),
    ("FC Twente Enschede", "Netherlands", "UEFA"),
    ("Querétaro FC", "Mexico", "CONCACAF"),
    ("Benfika Lizbona B", "Portugal", "UEFA"),
    ("AC Ajaccio", "France", "UEFA"),
    ("Melbourne Victory", "Australia", "AFC"),
    ("CSD Colo-Colo", "Chile", "CONMEBOL"),
    ("Zulte Waregem", "Belgium", "UEFA"),
    ("Brisbane Roar", "Australia", "AFC"),
    ("FK Austria Wiedeń", "Austria", "UEFA"),
    ("Panathinaikos FC", "Greece", "UEFA"),
    ("Independiente Santa Fe", "Colombia", "CONMEBOL"),
    ("CA San Lorenzo de Almagro", "Argentina", "CONMEBOL"),
    ("Caykur Rizespor", "Turkey", "UEFA"),
    ("Santos FC", "Brazil", "CONMEBOL"),
    ("Stabæk Fotball", "Norway", "UEFA"),
    ("Cagliari Calcio", "Italy", "UEFA"),
    ("Granada CF", "Spain", "UEFA"),
    ("TSV 1860 München", "Germany", "UEFA"),
    ("Shandong Luneng Taishan", "China", "AFC"),
    ("AS Saint-Étienne", "France", "UEFA"),
    ("AIK", "Sweden", "UEFA"),
    ("FC Utrecht", "Netherlands", "UEFA"),
    ("Sanfrecce Hiroshima", "Japan", "AFC"),
    ("AS Nancy-Lorraine", "France", "UEFA"),
    ("Catania Calcio", "Italy", "UEFA"),
    ("1.FC Nürnberg", "Germany", "UEFA"),
    ("Rosenborg BK", "Norway", "UEFA"),
    ("Júbilo Iwata", "Japan", "AFC"),
    ("Kubań Krasnodar (-2018)", "Russia", "UEFA"),
    ("Aalesunds FK", "Norway", "UEFA"),
    ("Parma FC", "Italy", "UEFA"),
    ("US Palermo", "Italy", "UEFA"),
    ("Real Zaragoza", "Spain", "UEFA"),
    ("Botafogo de Futebol e Regatas", "Brazil", "CONMEBOL"),
    ("Vitesse Arnhem", "Netherlands", "UEFA"),
    ("Deportivo Quito", "Ecuador", "CONMEBOL"),
    ("CS Emelec", "Ecuador", "CONMEBOL"),
    ("Barcelona SC Guayaquil", "Ecuador", "CONMEBOL"),
    ("CD Chivas USA", "United States", "CONCACAF"),
    ("CD Motagua Tegucigalpa", "Honduras", "CONCACAF"),
    ("SC Bastia", "France", "UEFA"),
    ("CD Olimpia", "Honduras", "CONCACAF"),
    ("CD Real Sociedad de Tocoa", "Honduras", "CONCACAF"),
    ("Wisła Kraków", "Poland", "UEFA"),
    ("Fethiyespor", "Turkey", "UEFA"),
    ("VfR Aalen", "Germany", "UEFA"),
    ("CD El Nacional", "Ecuador", "CONMEBOL"),
    ("Guizhou Renhe", "China", "AFC"),
    ("NEC Nijmegen", "Netherlands", "UEFA"),
    ("FK Borac Banja Luka", "Bosnia and Herzegovina", "UEFA"),
    ("Istanbul Büyüksehir Belediyespor", "Turkey", "UEFA"),
    ("Club Tijuana", "Mexico", "CONCACAF"),
    ("Gaziantepspor", "Turkey", "UEFA"),
    ("Kayseri Erciyesspor", "Turkey", "UEFA"),
    ("SK Sturm Graz", "Austria", "UEFA"),
    ("Eintracht Braunschweig", "Germany", "UEFA"),
    ("Naft Teheran", "Iran", "AFC"),
    ("CS Cartaginés", "Costa Rica", "CONCACAF"),
    ("SC Covilhã", "Portugal", "UEFA"),
    ("Zorya Lugansk", "Ukraine", "UEFA"),
    ("FC Zürich", "Switzerland", "UEFA"),
    ("Aduana Stars FC", "Ghana", "CAF"),
    ("Atlético Nacional", "Colombia", "CONMEBOL"),
    ("FC Évian Thonon Gaillard", "France", "UEFA"),
    ("FC Ashdod", "Israel", "UEFA"),
    ("Olympiakos Nikosia", "Cyprus", "UEFA"),
    ("Orlando Pirates", "South Africa", "CAF"),
    ("FC Sochaux-Montbéliard", "France", "UEFA"),
    ("Valenciennes FC", "France", "UEFA"),
    ("Mamelodi Sundowns FC", "South Africa", "CAF"),
    ("Charlton Athletic", "England", "UEFA"),
    ("Sporting Kansas City", "United States", "CONCACAF"),
    ("Foolad FC", "Iran", "AFC"),
    ("Lekhwiya SC", "Qatar", "AFC"),
    ("CS Constantine", "Algeria", "CAF"),
    ("USM Algier", "Algeria", "CAF"),
    ("Académica Coimbra", "Portugal", "UEFA"),
    ("Strømsgodset IF", "Norway", "UEFA"),
    ("Guangzhou Evergrande", "China", "AFC"),
    ("PAE Veria", "Greece", "UEFA"),
    ("Busan IPark", "South Korea", "AFC"),
    ("GFC Ajaccio", "France", "UEFA"),
    ("Guangzhou R&F", "China", "AFC"),
    ("Alania Vladikavkaz", "Russia", "UEFA"),
    ("Bolton Wanderers", "England", "UEFA"),
    ("Zenit St. Petersburg II", "Russia", "UEFA"),
    ("GFC Ajaccio", "France", "UEFA"),
    ("Guangzhou R&F", "China", "AFC"),
    ("Alania Vladikavkaz", "Russia", "UEFA"),
    ("Anży Machaczkała ( -2022)", "Russia", "UEFA"),
    ("AO Platanias", "Greece", "UEFA"),
    ("Atlético Mineiro", "Brazil", "CONMEBOL"),
    ("Moroka Swallows", "South Africa", "CAF"),
    ("CA Colón", "Argentina", "CONMEBOL"),
    ("Club Estudiantes de La Plata", "Argentina", "CONMEBOL"),
    ("Maccabi Haifa", "Israel", "UEFA"),
    ("Kaizer Chiefs", "South Africa", "CAF"),
    ("Jaguares de Chiapas", "Mexico", "CONCACAF"),
    ("Hapoel Tel Aviv", "Israel", "UEFA"),
    ("SuperSport United", "South Africa", "CAF"),
    ("Steaua Bukarest", "Romania", "UEFA"),
    ("Ajax Cape Town (- 2020)", "South Africa", "CAF"),
    ("Hapoel Petah Tikva", "Israel", "UEFA"),
    ("Lamontville Golden Arrows", "South Africa", "CAF"),
    ("Oita Trinita", "Japan", "AFC"),
    ("Maritzburg United FC", "South Africa", "CAF"),
    ("Krylja Sowietow Samara", "Russia", "UEFA"),
    ("Seongnam Ilhwa Chunma", "South Korea", "AFC"),
    ("Pohang Steelers", "South Korea", "AFC"),
    ("AC Siena", "Italy", "UEFA"),
    ("ES Sétif", "Algeria", "CAF"),
    ("ASO Chlef", "Algeria", "CAF"),
    ("Racing Santander", "Spain", "UEFA"),
    ("US Avellino", "Italy", "UEFA"),
    ("Busan I'Park", "South Korea", "AFC"),
    ("FC Istres Ouest Provence ", "France", "UEFA"),
    ("Kyoto Sanga", "Japan", "AFC"),
    ("Sparta Rotterdam", "Netherlands", "UEFA"),
    ("CD Nacional", "Portugal", "UEFA"),
    ("Grenoble Foot 38", "France", "UEFA"),
    ("AC Mantova 1911", "Italy", "UEFA"),
    ("Bnei Yehuda Tel Aviv", "Israel", "UEFA"),
    ("FK Moskwa", "Russia", "UEFA"),
    ("TuS Koblenz", "Germany", "UEFA"),
    ("IK Start", "Norway", "UEFA"),
    ("Blackburn Rovers", "England", "UEFA"),
    ("AE Larisa", "Greece", "UEFA"),
    ("Aarhus GF", "Denmark", "UEFA"),
    ("FC Groningen", "Netherlands", "UEFA"),
    ("AO Kavala", "Greece", "UEFA"),
    ("AC Arles-Avignon", "France", "UEFA"),
    ("Fredrikstad FK", "Norway", "UEFA"),
    ("NAC Breda", "Netherlands", "UEFA"),
    ("Gold Coast United", "Australia", "AFC"),
    ("FK Cukaricki", "Serbia", "UEFA"),
    ("MKE Ankaragücü", "Turkey", "UEFA"),
    ("NK Maribor", "Slovenia", "UEFA"),
    ("FK Vojvodina Novi Sad", "Serbia", "UEFA"),
    ("FK Hajduk Kula", "Serbia", "UEFA"),
    ("MSV Duisburg", "Germany", "UEFA"),
    ("KSV Roeselare (- 2020)", "Belgium", "UEFA"),
    ("Wellington Phoenix", "New Zealand", "OFC"),
    ("Auckland City FC", "New Zealand", "OFC"),
    ("Team Wellington (2004-2021)", "New Zealand", "OFC"),
    ("1.FC Kaiserslautern", "Germany", "UEFA"),
    ("Canterbury United (2002 - 2021)", "New Zealand", "OFC"),
    ("Argentinos Juniors", "Argentina", "CONMEBOL"),
    ("AC Sparta Praga", "Czech Republic", "UEFA"),
    ("Saturn Ramenskoe", "Russia", "UEFA"),
    ("FC Timisoara", "Romania", "UEFA"),
    ("AS Bari", "Italy", "UEFA"),
    ("Slovan Bratislava", "Slovakia", "UEFA"),
    ("US Grosseto FC", "Italy", "UEFA"),
    ("Club Libertad Asunción", "Paraguay", "CONMEBOL"),
    ("AC Cesena", "Italy", "UEFA"),
    ("Albirex Niigata", "Japan", "AFC"),
    ("FC Midtjylland", "Denmark", "UEFA"),
    ("SC Bastia B", "France", "UEFA"),
    ("Plymouth Argyle", "England", "UEFA"),
    ("Tom Tomsk", "Russia", "UEFA"),
    ("Reggina Calcio", "Italy", "UEFA"),
    ("Independiente Medellín", "Colombia", "CONMEBOL"),
    ("Iraklis Saloniki", "Greece", "UEFA"),
    ("Kansas City Wizards", "United States", "CONCACAF"),
    ("Hangzhou Greentown", "China", "AFC"),
    ("Skoda Xanthi", "Greece", "UEFA"),
    ("FC Vaslui", "Romania", "UEFA"),
    ("Club Necaxa", "Mexico", "CONCACAF"),
    ("FC International Curtea de Arges", "Romania", "UEFA"),
    ("CD Marathón", "Honduras", "CONCACAF"),
    ("Spartak Trnava", "Slovakia", "UEFA"),
    ("JEF United Chiba", "Japan", "AFC"),
    ("Slavia Sofia", "Bulgaria", "UEFA"),
    ("Xerez CD", "Spain", "UEFA"),
    ("Maccabi Netanya", "Israel", "UEFA"),
    ("Recreativo Huelva", "Spain", "UEFA"),
    ("Cracovia", "Poland", "UEFA"),
    ("Metalist Kharkiv", "Ukraine", "UEFA"),
    ("Elche CF", "Spain", "UEFA"),
    ("IFK Göteborg", "Sweden", "UEFA"),
    ("IF Elfsborg", "Sweden", "UEFA"),
    ("Dundee FC", "Scotland", "UEFA"),
    ("Falkirk FC", "Scotland", "UEFA"),
    ("FC Gillingham", "England", "UEFA"),
    ("Wrexham AFC", "Wales", "UEFA"),
    ("Coventry City", "England", "UEFA"),
    ("Crewe Alexandra", "England", "UEFA"),
    ("Port Vale FC", "England", "UEFA"),
    ("FC Hansa Rostock", "Germany", "UEFA"),
    ("CA Independiente II", "Argentina", "CONMEBOL"),
    ("New England Revolution", "United States", "CONCACAF"),
    ("SV Waldhof Mannheim", "Germany", "UEFA"),
    ("Roda JC Kerkrade", "Netherlands", "UEFA"),
    ("FC Sochaux-Montbéliard B", "France", "UEFA"),
    ("KSK Beveren (- 2010)", "Belgium", "UEFA"),
    ("Wisła Płock", "Poland", "UEFA"),
    ("Zeleznik Belgrad", "Serbia", "UEFA"),
    ("Viborg FF", "Denmark", "UEFA"),
    ("FC Messina Peloro", "Italy", "UEFA"),
    ("Terek Grozny", "Russia", "UEFA"),
    ("PAS Tehran", "Iran", "AFC"),
    ("Piroozi FC", "Iran", "AFC"),
    ("Saba Battery Qom", "Iran", "AFC"),
    ("Portimonense SC", "Portugal", "UEFA"),
    ("Hapoel Kfar Saba", "Israel", "UEFA"),
    ("Modena FC", "Italy", "UEFA"),
    ("Internacional Porto Alegre", "Brazil", "CONMEBOL"),
    ("King Faisal FC", "Ghana", "CAF"),
    ("Neuchâtel Xamax", "Switzerland", "UEFA"),
    ("Colorado Rapids", "United States", "CONCACAF"),
    ("D.C. United", "United States", "CONCACAF"),
    ("FC Energie Cottbus", "Germany", "UEFA"),
    ("Tecos de la UAG", "Mexico", "CONCACAF"),
    ("SG Dynamo Dresden", "Germany", "UEFA"),
    ("FC Barreirense", "Portugal", "UEFA"),
    ("Chunnam Dragons", "South Korea", "AFC"),
    ("AS Livorno", "Italy", "UEFA"),
    ("RAEC Mons (-2015)", "Belgium", "UEFA"),
    ("VfB Admira Wacker Mödling", "Austria", "UEFA"),
    ("Servette FC", "Switzerland", "UEFA"),
    ("SC YF Juventus Zürich", "Switzerland", "UEFA"),
    ("Bayer 04 Leverkusen U19", "Germany", "UEFA"),
    ("Derby County", "England", "UEFA"),
    ("Tromsø IL", "Norway", "UEFA"),
    ("Lierse SK (-2018)", "Belgium", "UEFA"),
    ("Gwangju Sangmu", "South Korea", "AFC"),
    ("Dnipro Dniepropetrowsk  (-2020)", "Ukraine", "UEFA"),
    ("Samsunspor", "Turkey", "UEFA"),
    ("Czornomoreć Odessa", "Ukraine", "UEFA"),
    ("Arsenał Kijów ( -2019)", "Ukraine", "UEFA"),
    ("Rot-Weiß Oberhausen", "Germany", "UEFA"),
    ("Vorskla Poltava", "Ukraine", "UEFA"),
    ("Dynamo-2 Kijów", "Ukraine", "UEFA"),
    ("Clermont Foot Auvergne", "France", "UEFA"),
    ("FC Aboomoslem", "Iran", "AFC"),
    ("MTK Budapest", "Hungary", "UEFA"),
    ("Újpest FC", "Hungary", "UEFA"),
    ("Kecskeméti TE", "Hungary", "UEFA"),
    ("Paksi FC", "Hungary", "UEFA"),
    ("US Lecce", "Italy", "UEFA"),
    ("Fehérvár FC", "Hungary", "UEFA"),
    ("Parma Calcio 1913", "Italy", "UEFA"),
    ("Le Havre AC", "France", "UEFA"),
    ("FC Empoli", "Italy", "UEFA"),
    ("Sivasspor", "Turkey", "UEFA"),
    ("FC Famalicão", "Portugal", "UEFA"),
    ("FC Baniyas", "United Arab Emirates", "AFC"),
    ("SV Darmstadt 98", "Germany", "UEFA"),
    ("Gwangju FC", "South Korea", "AFC"),
    ("NK Celje", "Slovenia", "UEFA"),
    ("Ulsan HD FC", "South Korea", "AFC"),
    ("FC Voluntari", "Romania", "UEFA"),
    ("Crawley Town", "England", "UEFA"),
    ("APOEL Nikosia", "Cyprus", "UEFA"),
    ("AS Cittadella", "Italy", "UEFA"),
    ("FK Bodø/Glimt", "Norway", "UEFA"),
    ("FK Sochi", "Russia", "UEFA"),
    ("CFR Cluj", "Romania", "UEFA"),
    ("FC Südtirol", "Italy", "UEFA"),
    ("Pisa Sporting Club", "Italy", "UEFA"),
    ("NK Olimpija Ljubljana", "Slovenia", "UEFA"),
    ("FK TSC Backa Topola", "Serbia", "UEFA"),
    ("Jagiellonia Białystok", "Poland", "UEFA"),
    ("Union Saint-Gilloise", "Belgium", "UEFA"),
    ("Puskás Akadémia FC", "Hungary", "UEFA"),
    ("TSV Hartberg", "Austria", "UEFA"),
    ("FC Banik Ostrava", "Czech Republic", "UEFA"),
    ("FC Slovan Liberec", "Czech Republic", "UEFA"),
    ("Hatta Club", "United Arab Emirates", "AFC"),
    ("Ascoli Calcio", "Italy", "UEFA"),
    ("Gaziantep FK", "Turkey", "UEFA"),
    ("Universitatea Craiova", "Romania", "UEFA"),
    ("Damac FC", "Saudi Arabia", "AFC"),
    ("KVC Westerlo", "Belgium", "UEFA"),
    ("Al-Okhdood Club", "Saudi Arabia", "AFC"),
    ("Palermo FC", "Italy", "UEFA"),
    ("Raków Częstochowa", "Poland", "UEFA"),
    ("Muaither SC", "Qatar", "AFC"),
    ("LASK", "Austria", "UEFA"),
    ("Polissya Zhytomyr", "Ukraine", "UEFA"),
    ("SK Slavia Praga", "Czech Republic", "UEFA"),
    ("Dinamo Tbilisi", "Georgia", "UEFA"),
    ("SK Dnipro-1", "Ukraine", "UEFA"),
    ("Karlsruher SC", "Germany", "UEFA"),
    ("Wolfsberger AC", "Austria", "UEFA"),
    ("Qarabağ FK", "Azerbaijan", "UEFA"),
    ("Dinamo Batumi", "Georgia", "UEFA"),
    ("FC Viktoria Pilzno", "Czech Republic", "UEFA"),
    ("FCSB", "Romania", "UEFA"),
    ("Manchester United U23", "England", "UEFA"),
    ("Kilmarnock FC", "Scotland", "UEFA"),
    ("HJK Helsinki", "Finland", "UEFA"),
    ("PEC Zwolle", "Netherlands", "UEFA"),
    ("BK Häcken", "Sweden", "UEFA"),
    ("Montreal Impact", "Canada", "CONCACAF"),
    ("SK Brann", "Norway", "UEFA"),
    ("Esbjerg fB", "Denmark", "UEFA"),
    ("Shanghai SIPG", "China", "AFC"),
    ("Lokomotiv-Kazanka Moskau", "Russia", "UEFA"),
    ("FC Honka", "Finland", "UEFA"),
    ("Bristol Rovers", "England", "UEFA"),
    ("Ajax Amsterdam U21", "Netherlands", "UEFA"),
    ("FK Ufa", "Russia", "UEFA"),
    ("Rabotnicki Skopje", "North Macedonia", "UEFA"),
    ("AEK Larnaka", "Cyprus", "UEFA"),
    ("MOL Vidi FC", "Hungary", "UEFA"),
    ("Nîmes Olympique", "France", "UEFA"),
    ("Shkendija Tetovo", "North Macedonia", "UEFA"),
    ("Vardar Skopje", "North Macedonia", "UEFA"),
    ("FC Nitra", "Slovakia", "UEFA"),
    ("MFK Ruzomberok", "Slovakia", "UEFA"),
    ("KV Kortrijk", "Belgium", "UEFA"),
    ("Sönderjyske", "Denmark", "UEFA"),
    ("Helsingborgs IF", "Sweden", "UEFA"),
    ("FK Sarajevo", "Bosnia and Herzegovina", "UEFA"),
    ("SK Sigma Ołomuniec", "Czech Republic", "UEFA"),
    ("SK Sigma Olomouc U19", "Czech Republic", "UEFA"),
    ("Śląsk Wrocław", "Poland", "UEFA"),
    ("Motherwell FC", "Scotland", "UEFA"),
    ("Dunfermline Athletic FC", "Scotland", "UEFA"),
    ("Dalian Professional", "China", "AFC"),
    ("Genclerbirligi Ankara", "Turkey", "UEFA"),
    ("Anorthosis Famagusta", "Cyprus", "UEFA"),
    ("Livingston FC", "Scotland", "UEFA"),
    ("Apollon Limassol", "Cyprus", "UEFA"),
    ("Mezőkövesd Zsóry FC", "Hungary", "UEFA"),
    ("Zalaegerszegi TE FC", "Hungary", "UEFA"),
    ("Budapest Honvéd FC", "Hungary", "UEFA"),
    ("Debreceni VSC", "Hungary", "UEFA"),
    ("SK Dynamo Czeskie Budziejowice", "Czech Republic", "UEFA"),
    ("PAS Giannina", "Greece", "UEFA"),
    ("Osmanlispor FK", "Turkey", "UEFA"),
    ("Frosinone Calcio", "Italy", "UEFA"),
    ("Delfino Pescara 1936", "Italy", "UEFA"),
    ("KF Skënderbeu", "Albania", "UEFA"),
    ("Pandurii Targu Jiu (- 2022)", "Romania", "UEFA"),
    ("Córdoba CF", "Spain", "UEFA"),
    ("Astra Giurgiu", "Romania", "UEFA"),
    ("Inverness Caledonian Thistle FC", "Scotland", "UEFA"),
    ("FK Jablonec", "Czech Republic", "UEFA"),
    ("Kairat Almaty", "Kazakhstan", "UEFA"),
    ("FC Vaduz", "Liechtenstein", "UEFA"),
    ("FK Partizani", "Albania", "UEFA"),
    ("Willem II Tilburg", "Netherlands", "UEFA"),
    ("MSK Zilina", "Slovakia", "UEFA"),
    ("Ruch Chorzów", "Poland", "UEFA"),
    ("Zagłębie Lubin", "Poland", "UEFA"),
    ("Fleetwood Town", "England", "UEFA"),
    ("Hamilton Academical FC", "Scotland", "UEFA"),
    ("Doncaster Rovers", "England", "UEFA"),
    ("Calcio Como", "Italy", "UEFA"),
    ("Notts County", "England", "UEFA"),
    ("Sheffield Wednesday", "England", "UEFA"),
    ("Sandefjord Fotball", "Norway", "UEFA"),
    ("IFK Norrköping", "Sweden", "UEFA"),
    ("Molde FK", "Norway", "UEFA"),
    ("GIF Sundsvall", "Sweden", "UEFA"),
    ("FC Ingolstadt 04", "Germany", "UEFA"),
    ("Diósgyőri VTK", "Hungary", "UEFA"),
    ("Videoton FC", "Hungary", "UEFA"),
    ("Szombathelyi Haladás", "Hungary", "UEFA"),
    ("Al-Sailiya SC", "Qatar", "AFC"),
    ("FK Baumit Jablonec", "Czech Republic", "UEFA"),
    ("Worskła Połtawa", "Ukraine", "UEFA"),
    ("Illicziweć Mariupol", "Ukraine", "UEFA"),
    ("Cheltenham Town", "England", "UEFA"),
    ("SK Tawrija Symferopol (-2022)", "Ukraine", "UEFA"),
    ("Hamarkameratene", "Norway", "UEFA"),
    ("GKS Bełchatów", "Poland", "UEFA"),
    ("SV Mattersburg", "Austria", "UEFA"),
    ("Ankaraspor", "Turkey", "UEFA"),
    ("Korona Kielce", "Poland", "UEFA"),
    ("OFI Kreta", "Greece", "UEFA"),
    ("Rapid Bukarest", "Romania", "UEFA"),
    ("CSKA Sofia", "Bulgaria", "UEFA"),
    ("Politehnica Timișoara", "Romania", "UEFA")
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


async def get_ranking(session, federation, country, year, confederation_multiplier):
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
        return 0

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

    final_ranking = ranking * confederation_multiplier

    return final_ranking


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

    # Definiowanie współczynników dla każdej konfederacji
    confederation_multipliers = {
        "UEFA": 54,
        "CONMEBOL": 39,
        "AFC": 11,
        "CAF": 8,
        "CONCACAF": 7,
        "OFC": 1
    }

    # Cache dla rankingów
    ranking_cache = {}

    async with aiohttp.ClientSession() as session:
        for (club,) in clubs:
            # Znajdź kraj i federację dla klubu
            team_info = next((info for info in football_teams_info if info[0] == club), None)

            if team_info:
                country = team_info[1]
                federation = team_info[2]

                if (federation, country) not in ranking_cache:
                    # Jeśli ranking dla tej federacji i kraju nie jest w cache, oblicz go
                    confederation_multiplier = confederation_multipliers.get(federation, 1)
                    ranking = await get_ranking(session, federation, country, year, confederation_multiplier)
                    ranking_cache[(federation, country)] = ranking
                else:
                    # Pobierz ranking z cache
                    ranking = ranking_cache[(federation, country)]

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
                position_element = soup.select_one(
                    "#tm-main > header > div.data-header__info-box > div > ul:nth-child(2) > li:nth-child(2) > span"
                )
                position = position_element.text.strip() if position_element else "Unknown"

                # Sprawdzenie, czy zawodnik jest bramkarzem
                is_goalkeeper = "Goalkeeper" in position

                # Próbujemy pobrać dane ze statystyk z różnych możliwych ścieżek
                tfoot = soup.find('tfoot')
                if not tfoot:
                    # Próba innej metody wyszukania tabeli, jeśli tfoot nie istnieje
                    stats_table = soup.select("div.responsive-table > table > tbody > tr > td")
                else:
                    stats_table = tfoot.find_all('td')

                if stats_table and len(stats_table) > 0:
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
                            "appearances": appearances if appearances != "-" else '0',
                            "clean_sheets": clean_sheets if clean_sheets != "-" else '0',
                            "conceded_goals": conceded_goals if conceded_goals != "-" else '0',
                            "yellow_cards": yellow_cards if yellow_cards != "-" else '0',
                            "red_cards": red_cards if red_cards != "-" else '0',
                            "minutes_played": minutes_played if minutes_played != "-" else '0',
                            "position": position
                        }
                    else:
                        # Statystyki dla zawodników z pola
                        minutes_played = stats_table[7].text.strip().replace(".", "").replace("'", "") or '0'
                        stats = {
                            "appearances": stats_table[3].text.strip() if stats_table[3].text.strip() != "-" else '0',
                            "goals": stats_table[4].text.strip() if stats_table[4].text.strip() != "-" else '0',
                            "assists": stats_table[5].text.strip() if stats_table[5].text.strip() != "-" else '0',
                            "yellow_cards": stats_table[6].text.strip().split("/")[0].strip() if stats_table[6].text.strip().split("/")[0].strip() != "-" else '0',
                            "red_cards": stats_table[6].text.strip().split("/")[1].strip() if stats_table[6].text.strip().split("/")[1].strip() != "-" else '0',
                            "minutes_played": minutes_played if minutes_played != "-" else '0',
                            "position": position
                        }

                    return stats
                else:
                    print(f"No stats found in tfoot or alternative path for player ID {player_id}.")
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

def remove_players_without_stats(conn):
    cursor = conn.cursor()

    # Zbieranie transfermarkt_id graczy, którzy mają pustą wartość w kolumnie 'position' w market_value_history
    cursor.execute("""
    SELECT DISTINCT player_id 
    FROM market_value_history 
    WHERE position IS NULL
    """)
    players_to_remove = cursor.fetchall()

    if not players_to_remove:
        print("Nie znaleziono graczy do usunięcia.")
        return

    players_to_remove = [row[0] for row in players_to_remove]

    print("IDs to be removed due to missing position:", players_to_remove)

    # Usunięcie graczy z tabeli teams
    cursor.executemany("DELETE FROM teams WHERE transfermarkt_id = ?", [(player_id,) for player_id in players_to_remove])
    print(f"Usunięto {cursor.rowcount} graczy z tabeli teams.")

    # Usunięcie graczy z tabeli market_value_history
    cursor.executemany("DELETE FROM market_value_history WHERE player_id = ?", [(player_id,) for player_id in players_to_remove])
    print(f"Usunięto {cursor.rowcount} wpisów z tabeli market_value_history.")

    conn.commit()



# Call this function in your scraping process
def run_scraping_process(year, tournament, event_date):
    try:
        tournament = tournament
        year = year
        event_date = event_date
        conn = create_database(tournament, year)
        print("Baza danych została utworzona.")

        if tournament == "world_cup1":
            # Pobranie danych drużyn
            scrap_squad(f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_squads", conn)
            print("Dane drużyn zostały pobrane i zapisane do bazy danych.")

        if tournament == "euro1":
            # Pobranie danych drużyn
            scrap_squad(f"https://en.wikipedia.org/wiki/UEFA_Euro_{year}_squads", conn)
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
        save_market_value_history(player_ids, conn, event_date)
        print("Historia wartości rynkowej została pobrana i zapisana.")

        # Dodajemy informacje o federacji, kraju i rankingu do market_value_history
        asyncio.run(update_market_value_history_with_rankings(conn, football_teams_info, year-1))
        print("Informacje o federacji, kraju i rankingu zostały zaktualizowane.")

        # Pobieranie i zapisywanie statystyk zawodników
        save_player_stats(player_ids, year-1, conn)
        print("Statystyki zawodników zostały pobrane i zapisane.")

        # Usunięcie graczy bez statystyk
        remove_players_without_stats(conn)
        print("Gracze bez statystyk zostali usunięci.")

        # Zamknięcie połączenia z bazą danych
        conn.close()
        print("Połączenie z bazą danych zostało zamknięte.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")


# Wywołanie funkcji głównej, aby uruchomić cały proces dla konkretnego roku
# run_scraping_process(2022, "world_cup1", "20-11-2022")
# run_scraping_process(2018, "world_cup1", "14-06-2018")
# run_scraping_process(2014, "world_cup1", "12-06-2014")
# run_scraping_process(2010, "world_cup1", "11-06-2010")
# run_scraping_process(2006, "world_cup1", "09-06-2006")
# run_scraping_process(2024, "euro1", "14-06-2024")
# run_scraping_process(2020, "euro1", "11-06-2020")
# run_scraping_process(2016, "euro1", "10-06-2016")
# run_scraping_process(2012, "euro1", "08-06-2012")
# run_scraping_process(2008, "euro1", "07-06-2008")
