import asyncio
import datetime
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
        "Dušan Petković[29]": "Dusan Petkovic",
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
        "Musab Kheder": "Musab Khoder",
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
         "Munir Mohamedi": "Munir El Kajoui"
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

                        if market_value == "-" or not date_mv:
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








club_name_mapping = {
    "Leverkusen": "Bayer 04 Leverkusen",
    "Man City": "Manchester City",
    "Arsenal": "FC Arsenal",
    "Newcastle": "Newcastle United",
    "Sheffield United": "Sheffield United",
    "Brighton": "Brighton & Hove Albion",
    "Monaco": "AS Monaco",
    "PSV": "PSV Eindhoven",
    "Valencia": "Valencia CF",
    "Ajax": "Ajax Amsterdam",
    "Dortmund": "Borussia Dortmund",
    "Juventus": "Juventus Turyn",
    "Luton": "Luton Town",
    "Fulham": "FC Fulham",
    "Leeds": "Leeds United",
    "Chelsea": "Chelsea FC",
    "Milan": "AC Milan",
    "Barcelona": "FC Barcelona",
    "Feyenoord": "Feyenoord Rotterdam",
    "Lille": "LOSC Lille",
    "Rennes": "Stade Rennais FC",
    "Brentford": "FC Brentford",
    "Gladbach": "Borussia Mönchengladbach",
    "Watford": "FC Watford",
    "Tottenham": "Tottenham Hotspur",
    "Swansea": "Swansea City",
    "Lyon": "Olympique Lyon",
    "Villarreal": "Villarreal CF",
    "Atlético": "Atlético Madryt",
    "Sevilla": "Sevilla FC",
    "Betis": "Real Betis Balompié",
    "Paris SG": "FC Paris Saint-Germain",
    "Roma": "AS Roma",
    "Atalanta": "Atalanta BC",
    "Genk": "KRC Genk",
    "Wolves": "Wolverhampton Wanderers",
    "Forest": "Nottingham Forest",
    "Celtic": "Celtic Glasgow",
    "Wolfsburg": "VfL Wolfsburg",
    "Celta": "Celta de Vigo",
    "Napoli": "SSC Napoli",
    "Bournemouth": "AFC Bournemouth",
    "Aston Villa": "Aston Villa",
    "Burnley": "FC Burnley",
    "Inter": "Inter Mediolan",
    "Lech": "Lech Poznań",
    "Lens": "RC Lens",
    "Fiorentina": "AC Fiorentina",
    "Sampdoria": "UC Sampdoria",
    "Nice": "OGC Nice",
    "Cardiff": "Cardiff City",
    "Union Berlin": "1.FC Union Berlin",
    "RB Leipzig": "RasenBallsport Leipzig",
    "Hertha": "Hertha BSC",
    "Man United": "Manchester United",
    "Real Madrid": "Real Madryt",
    "Bayern": "Bayern Monachium",
    "Liverpool": "FC Liverpool",
    "Frankfurt": "Eintracht Frankfurt",
    "Galatasaray": "Galatasaray",
    "Verona": "Hellas Verona",
    "Legia": "Legia Warszawa",
    "Millonarios FC": "Millonarios FC",
    "Marseille": "Olympique Marseille",
    "West Ham": "West Ham United",
    "Freiburg": "SC Freiburg",
    "Köln": "1.FC Köln",
    "Real Sociedad": "Real Sociedad",
    "Southampton": "FC Southampton",
    "Sporting": "Sporting CP",
    "Schalke": "FC Schalke 04",
    "Stuttgart": "VfB Stuttgart",
    "Bilbao": "Athletic Bilbao",
    "Hoffenheim": "TSG 1899 Hoffenheim",
    "Fenerbahçe": "Fenerbahce",
    "Beşiktaş": "Besiktas JK",
    "Anderlecht": "RSC Anderlecht",
    "Basel": "FC Basel 1893",
    "Dinamo Zagreb": "GNK Dinamo Zagrzeb",
    "Torino": "Torino FC",
    "Rangers": "Glasgow Rangers",
    "Зенит": "Zenit Petersburg",
    "Osasuna": "CA Osasuna",
    "Salzburg": "Red Bull Salzburg",
    "Toulouse": "FC Toulouse",
    "Reims": "Stade Reims",
    "Nantes": "FC Nantes",
    "Bristol City": "Bristol City",
    "Getafe": "Getafe CF",
    "Benevento": "Benevento Calcio",
    "Montpellier": "Montpellier HSC",
    "Trabzonspor": "Trabzonspor",
    "Espanyol": "RCD Espanyol",
    "Burgos": "Burgos CF",
    "Gent": "KAA Gent",
    "Udinese": "Udinese Calcio",
    "Standard": "Standard Liège",
    "Valladolid": "Real Valladolid CF",
    "Chicago Fire FC": "Chicago Fire FC",
    "Rayo Vallecano": "Rayo Vallecano",
    "ΠΑΟΚ": "PAOK Saloniki"
}

kluby = {
    "Royal Antwerpia FC": "Royal Antwerpia FC",
    "FC Augsburg": "FC Augsburg",
    "Al-Duhail SC": "Al-Duhail SC",
    "Al-Rayyan SC": "Al-Rayyan SC",
    "Los Angeles FC": "Los Angeles FC",
    "Al-Wakrah SC": "Al-Wakrah SC",
    "Al-Sadd SC": "Al-Sadd SC",
    "Santos Laguna": "Santos Laguna",
    "Al-Arabi SC": "Al-Arabi SC",
    "Independiente del Valle": "Independiente del Valle",
    "Queens Park Rangers": "Queens Park Rangers",
    "FC Everton": "FC Everton",
    "Vitoria Guimarães SC": "Vitoria Guimarães SC",
    "Leicester City": "Leicester City",
    "Al-Gharafa SC": "Al-Gharafa SC",
    "FC Reading": "FC Reading",
    "Amiens SC": "Amiens SC",
    "Pafos FC": "Pafos FC",
    "LDU Quito": "LDU Quito",
    "FC Sao Paulo": "FC Sao Paulo",
    "Club León FC": "Club León FC",
    "Seattle Sounders FC": "Seattle Sounders FC",
    "SC Heerenveen": "SC Heerenveen",
    "Persepolis FC": "Persepolis FC",
    "US Salernitana 1919": "US Salernitana 1919",
    "Esteghlal FC": "Esteghlal FC",
    "AEK Ateny": "AEK Ateny",
    "FC Brügge": "FC Brügge",
    "Sepahan FC": "Sepahan FC",
    "Imbabura SC": "Imbabura SC",
    "Omonia Nikozja": "Omonia Nikozja",
    "SD Aucas": "SD Aucas",
    "R Charleroi SC": "R Charleroi SC",
    "Al-Ahli SC": "Al-Ahli SC",
    "Tractor Sazi FC": "Tractor Sazi FC",
    "Nashville SC": "Nashville SC",
    "SD Ponferradina": "SD Ponferradina",
    "Shabab Al-Ahli Club": "Shabab Al-Ahli Club",
    "FC Dallas": "FC Dallas",
    "Kayserispor": "Kayserispor",
    "Inter Miami CF": "Inter Miami CF",
    "New York Red Bulls": "New York Red Bulls",
    "Vejle Boldklub": "Vejle Boldklub",
    "ESTAC Troyes": "ESTAC Troyes",
    "Norwich City": "Norwich City",
    "Swindon Town": "Swindon Town",
    "Dundee United FC": "Dundee United FC",
    "Atlanta United FC": "Atlanta United FC",
    "Airbus UK Broughton": "Airbus UK Broughton",
    "Milton Keynes Dons": "Milton Keynes Dons",
    "New York City FC": "New York City FC",
    "CA River Plate": "CA River Plate",
    "CF Pachuca": "CF Pachuca",
    "CA Newell's Old Boys": "CA Newell's Old Boys",
    "AFC Wimbledon": "AFC Wimbledon",
    "FC Juárez": "FC Juárez",
    "CF América": "CF América",
    "US Cremonese": "US Cremonese",
    "Spezia Calcio": "Spezia Calcio",
    "CF Monterrey": "CF Monterrey",
    "Huddersfield Town": "Huddersfield Town",
    "Houston Dynamo FC": "Houston Dynamo FC",
    "Deportivo Guadalajara": "Deportivo Guadalajara",
    "FC Portsmouth": "FC Portsmouth",
    "Al-Nassr FC": "Al-Nassr FC",
    "Al-Hilal SFC": "Al-Hilal SFC",
    "Al-Shabab FC": "Al-Shabab FC",
    "Birmingham City": "Birmingham City",
    "Charlotte FC": "Charlotte FC",
    "FC Kopenhaga": "FC Kopenhaga",
    "Pogoń Szczecin": "Pogoń Szczecin",
    "Al-Fateh SC": "Al-Fateh SC",
    "Melbourne City FC": "Melbourne City FC",
    "Heart of Midlothian FC": "Heart of Midlothian FC",
    "Cádiz CF": "Cádiz CF",
    "Brescia Calcio": "Brescia Calcio",
    "Al-Ittihad Club": "Al-Ittihad Club",
    "AFC Sunderland": "AFC Sunderland",
    "FC Middlesbrough": "FC Middlesbrough",
    "St. Mirren FC": "St. Mirren FC",
    "FC St. Pauli": "FC St. Pauli",
    "Central Coast Mariners": "Central Coast Mariners",
    "Adelaide United": "Adelaide United",
    "Bröndby IF": "Bröndby IF",
    "Columbus Crew": "Columbus Crew",
    "Odense Boldklub": "Odense Boldklub",
    "SV Schalding-Heining": "SV Schalding-Heining",
    "Stoke City": "Stoke City",
    "Fagiano Okayama": "Fagiano Okayama",
    "Sydney FC": "Sydney FC",
    "Kuwait SC": "Kuwait SC",
    "CS Sfaxien": "CS Sfaxien",
    "Ferencvárosi TC": "Ferencvárosi TC",
    "FC Lorient": "FC Lorient",
    "Etoile Sportive du Sahel": "Etoile Sportive du Sahel",
    "Esperance Tunis": "Esperance Tunis",
    "Millonarios FC": "Millonarios FC",
    "US Monastir": "US Monastir",
    "Atromitos Ateny": "Atromitos Ateny",
    "Club Africain Tunis": "Club Africain Tunis",
    "El Ahly Kair": "El Ahly Kair",
    "Al-Ettifaq FC": "Al-Ettifaq FC",
    "SM Caen": "SM Caen",
    "Zamalek SC": "Zamalek SC",
    "CD Leganés": "CD Leganés",
    "VfL Bochum": "VfL Bochum",
    "Fortuna Düsseldorf": "Fortuna Düsseldorf",
    "VV St. Truiden": "VV St. Truiden",
    "Cercle Brügge": "Cercle Brügge",
    "Shimizu S-Pulse": "Shimizu S-Pulse",
    "Nagoya Grampus": "Nagoya Grampus",
    "Shonan Bellmare": "Shonan Bellmare",
    "Urawa Red Diamonds": "Urawa Red Diamonds",
    "Kawasaki Frontale": "Kawasaki Frontale",
    "Deportivo Saprissa": "Deportivo Saprissa",
    "FC Cincinnati": "FC Cincinnati",
    "Municipal Grecia": "Municipal Grecia",
    "SV Werder Bremen": "SV Werder Bremen",
    "KMSK Deinze": "KMSK Deinze",
    "Minnesota United FC": "Minnesota United FC",
    "Vancouver Whitecaps FC": "Vancouver Whitecaps FC",
    "GD Chaves": "GD Chaves",
    "Austin FC": "Austin FC",
    "CF Montréal": "CF Montréal",
    "Toronto FC": "Toronto FC",
    "St. Johnstone FC": "St. Johnstone FC",
    "RC Strasbourg Alsace": "RC Strasbourg Alsace",
    "US Sassuolo": "US Sassuolo",
    "Panetolikos GFS": "Panetolikos GFS",
    "Real Salt Lake City": "Real Salt Lake City",
    "CD Lugo": "CD Lugo",
    "NK Osijek": "NK Osijek",
    "Al-Wehda FC": "Al-Wehda FC",
    "AD Guanacasteca": "AD Guanacasteca",
    "Wydad Casablanca": "Wydad Casablanca",
    "Qatar SC": "Qatar SC",
    "Angers SCO": "Angers SCO",
    "UNAM Pumas": "UNAM Pumas",
    "FC Tokyo": "FC Tokyo",
    "Sociedade Esportiva Palmeiras": "Sociedade Esportiva Palmeiras",
    "Stade Brestois 29": "Stade Brestois 29",
    "SSC Bari": "SSC Bari",
    "Colombe Sportive du Dja et Lobo": "Colombe Sportive du Dja et Lobo",
    "Olympiakos Pireus": "Olympiakos Pireus",
    "Aris Saloniki": "Aris Saloniki",
    "Abha Club": "Abha Club",
    "Coton Sport FC de Garoua": "Coton Sport FC de Garoua",
    "Lazio Rzym": "Lazio Rzym",
    "RCD Mallorca": "RCD Mallorca",
    "Crvena Zvezda Belgrad": "Crvena Zvezda Belgrad",
    "UD Almería": "UD Almería",
    "SC Braga": "SC Braga",
    "Al-Tai FC": "Al-Tai FC",
    "Dynamo Moskwa": "Dynamo Moskwa",
    "Philadelphia Union": "Philadelphia Union",
    "HNK Hajduk Split": "HNK Hajduk Split",
    "Hannover 96": "Hannover 96",
    "Shanghai Shenhua": "Shanghai Shenhua",
    "KV Mechelen": "KV Mechelen",
    "1.FSV Mainz 05": "1.FSV Mainz 05",
    "FC St. Gallen 1879": "FC St. Gallen 1879",
    "FC Bologna": "FC Bologna",
    "BSC Young Boys": "BSC Young Boys",
    "FC Luzern": "FC Luzern",
    "KAS Eupen": "KAS Eupen",
    "Asante Kotoko SC": "Asante Kotoko SC",
    "Clermont Foot 63": "Clermont Foot 63",
    "AJ Auxerre": "AJ Auxerre",
    "Jeonbuk Hyundai Motors": "Jeonbuk Hyundai Motors",
    "Gimcheon Sangmu": "Gimcheon Sangmu",
    "Gamba Osaka": "Gamba Osaka",
    "Daegu FC": "Daegu FC",
    "FC Seoul": "FC Seoul",
    "Daejeon Hana Citizen": "Daejeon Hana Citizen",
    "Ulsan Hyundai": "Ulsan Hyundai",
    "Hearts of Oak": "Hearts of Oak",
    "FC Porto": "FC Porto",
    "Club Nacional": "Club Nacional",
    "Flamengo Rio de Janeiro": "Flamengo Rio de Janeiro",
    "CA Independiente": "CA Independiente",
    "Orlando City SC": "Orlando City SC",
    "CA Vélez Sarsfield": "CA Vélez Sarsfield",
    "Club Athletico Paranaense": "Club Athletico Paranaense",
    "Los Angeles Galaxy": "Los Angeles Galaxy",
    "FC Lugano": "FC Lugano",
    "Shandong Taishan": "Shandong Taishan",
    "Chicago Fire FC": "Chicago Fire FC",
    "Benfika Lizbona": "Benfika Lizbona"
}

def fetch_elo_ranking_from_web(date):
    url = f"http://clubelo.com/{date}/Ranking"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Błąd podczas pobierania ELO rankingów dla {date}: {response.status_code}")
        return None


def parse_elo_ranking(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    ranking_table = soup.find("table", {"class": "ranking"})  # Znajdź tabelę z rankingiem

    elo_data = []
    if ranking_table:
        rows = ranking_table.find_all("tr")
        for row in rows[1:]:  # Pomijamy pierwszy wiersz, który zawiera nagłówki
            cols = row.find_all("td")
            if len(cols) >= 4:
                rank = cols[0].text.strip()

                # Pobierz nazwę klubu z elementu <a> wewnątrz <td class="l">
                club_name_element = cols[1].find("a")
                club_name = club_name_element.text.strip() if club_name_element else "N/A"

                elo_rating = cols[2].text.strip()  # ELO w trzeciej kolumnie

                print(f"Przetwarzanie: {club_name}, ELO: {elo_rating}")

                # Dodaj dane do listy
                elo_data.append({
                    "rank": rank,
                    "club_name": club_name,
                    "elo_rating": float(elo_rating)
                })
    else:
        print("Nie znaleziono tabeli z rankingiem")

    return elo_data


def update_market_value_history_with_elo(elo_data, conn):
    cursor = conn.cursor()
    for club in elo_data:
        club_name = club['club_name']
        elo_rating = club['elo_rating']

        # Generate club hash directly from the normalized club name
        normalized_club_name = club_name_mapping.get(club_name, club_name)
        normalized_hash = generate_team_id(normalized_club_name)
        print(f"Klub: {normalized_club_name}, hash: {normalized_hash}")

        # Search using the club hash
        sql_select = '''
            SELECT club_hash FROM market_value_history
            WHERE club_hash = ?
        '''
        cursor.execute(sql_select, (normalized_hash,))
        result = cursor.fetchone()

        if result:
            # Update ELO rating in the database
            sql_update = '''
                UPDATE market_value_history
                SET elo_rating = ?
                WHERE club_hash = ?
            '''
            print(f"SQL Update: {sql_update} with values ({elo_rating}, {normalized_hash})")
            cursor.execute(sql_update, (elo_rating, normalized_hash))
            print(f"Zaktualizowano klub: {club_name} z ELO: {elo_rating}")
        else:
            print(f"Nie znaleziono klubu: {club_name} (szukano: {normalized_club_name})")

    conn.commit()


def add_elo_column_to_market_value_history(conn):
    cursor = conn.cursor()

    # Sprawdzenie, czy kolumna 'elo_rating' już istnieje
    cursor.execute("PRAGMA table_info(market_value_history)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'elo_rating' not in columns:
        # Jeśli kolumna nie istnieje, dodajemy ją
        cursor.execute('''
            ALTER TABLE market_value_history
            ADD COLUMN elo_rating REAL
        ''')
        conn.commit()
        print("Kolumna 'elo_rating' została dodana do tabeli 'market_value_history'.")
    else:
        print("Kolumna 'elo_rating' już istnieje w tabeli 'market_value_history'.")







# Uruchomienie całego procesu
# Uruchomienie całego procesu
def run_scraping_process():
    try:
        tournament = "world_cup1"
        conn = create_database(tournament, 2022)
        print("Baza danych została utworzona.")

        # Dodanie kolumny hashy klubów (jeśli nie została wcześniej dodana)
        add_club_hash_column_to_market_value_history(conn)
        print("Kolumna hashów klubów została dodana (jeśli nie istniała).")

        # Dodanie kolumny ELO do tabeli market_value_history (jeśli nie została wcześniej dodana)
        add_elo_column_to_market_value_history(conn)
        print("Kolumna ELO została dodana (jeśli nie istniała).")

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

        # Pobierz dane ELO z konkretnej daty
        date = "2022-11-20"
        html_content = fetch_elo_ranking_from_web(date)

        if html_content:
            elo_data = parse_elo_ranking(html_content)
            update_market_value_history_with_elo(elo_data, conn)
            print("Dane ELO zostały zaktualizowane.")

        # Zamknięcie połączenia z bazą danych
        conn.close()
        print("Połączenie z bazą danych zostało zamknięte.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

# Wywołanie funkcji głównej, aby uruchomić cały proces
run_scraping_process()
