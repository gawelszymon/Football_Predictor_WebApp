from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import sqlite3

# Funkcja do oczyszczania nazw drużyn
def clean_team_name(name):
    words_to_remove = ["Zwycięzca", "Awans"]
    for word in words_to_remove:
        name = name.replace(word, "").strip()
    return name

# Ścieżka do chromedrivera
driver_path = 'C:/webdriver/chromedriver-win64/chromedriver.exe'  # Zaktualizuj do prawidłowej ścieżki do chromedriver

# Opcje Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uruchom Chrome w tle

# Tworzenie instancji serwisu Chrome
service = Service(driver_path)

# Inicjalizacja przeglądarki z użyciem Service i opcji
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL do skrapowania
url = "https://www.flashscore.pl/pilka-nozna/swiat/mistrzostwa-swiata-2022/wyniki/"
driver.get(url)

# Czekanie na pełne załadowanie strony
time.sleep(5)  # Możesz dostosować czas w zależności od szybkości ładowania strony

# Pobranie źródła strony
page_source = driver.page_source

# Analiza HTML przy użyciu BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Znajdowanie wszystkich meczów na stronie
matches = soup.find_all('div', class_='event__match')

# Inicjalizacja licznika
match_count = 0

# Połączenie z bazą danych SQLite
conn = sqlite3.connect('world_cup_2022_results.db')
cursor = conn.cursor()

# Tworzenie tabeli, jeśli nie istnieje
cursor.execute('''
CREATE TABLE IF NOT EXISTS match_results (
    team_id1 TEXT,
    team_id2 TEXT,
    goals_team_id1 INTEGER,
    goals_team_id2 INTEGER,
    team1_stats TEXT,
    team2_stats TEXT
)
''')

# Przetwarzanie meczów z ograniczeniem do 31
for match in matches:
    if match_count >= 64:
        break

    # Pobieranie nazw drużyn
    home_team = clean_team_name(match.find('div', class_='event__homeParticipant').get_text(strip=True))
    away_team = clean_team_name(match.find('div', class_='event__awayParticipant').get_text(strip=True))

    # Pobieranie wyniku meczu
    home_score = match.find('div', class_='event__score--home').get_text(strip=True)
    away_score = match.find('div', class_='event__score--away').get_text(strip=True)

    # Pobieranie linku do szczegółów meczu i kodu meczu
    match_link = match.find('a', class_='eventRowLink')['href']
    match_code = re.search(r'\/mecz\/(.*?)\/', match_link).group(1)

    # Tworzenie URL do szczegółów statystyk
    stats_url = f"https://www.flashscore.pl/mecz/{match_code}/#/szczegoly-meczu/statystyki-meczu/0"

    # Odwiedzenie strony z detalami meczu
    driver.get(stats_url)
    time.sleep(5)  # Czekanie na załadowanie strony ze statystykami

    # Pobranie źródła strony
    stats_page_source = driver.page_source

    # Analiza HTML przy użyciu BeautifulSoup
    stats_soup = BeautifulSoup(stats_page_source, 'html.parser')

    # Pobieranie statystyk meczu
    stats_divs = stats_soup.find_all('div', class_='_row_ciop9_8')

    # Inicjalizacja zmiennych dla statystyk
    team1_stats = ''
    team2_stats = ''

    for stat in stats_divs:
        category = stat.find('div', class_='_category_y3bbr_4').get_text(strip=True)
        home_value = stat.find('div', class_='_homeValue_udiib_9').get_text(strip=True)
        away_value = stat.find('div', class_='_awayValue_udiib_13').get_text(strip=True)
        team1_stats += f'{category}: {home_value} | '
        team2_stats += f'{category}: {away_value} | '

    # Usuwanie niepotrzebnych separatorów na końcu
    team1_stats = team1_stats.strip(' |')
    team2_stats = team2_stats.strip(' |')

    # Zapisywanie wyników do bazy danych
    try:
        cursor.execute('''
        INSERT INTO match_results (
            team_id1, team_id2, goals_team_id1, goals_team_id2,
            team1_stats, team2_stats
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            home_team, away_team, home_score, away_score,
            team1_stats, team2_stats
        ))

        # Potwierdzenie zapisu
        print(f'Data saved: {home_team} {home_score} - {away_team} {away_score}')
        print(f'Team 1 Stats: {team1_stats}')
        print(f'Team 2 Stats: {team2_stats}')
        print('-' * 50)

    except sqlite3.Error as e:
        print(f"Error while inserting data: {e}")

    # Zwiększenie licznika
    match_count += 1

# Zatwierdzenie zmian
conn.commit()

# Wyświetlanie wyników w konsoli
try:
    cursor.execute('SELECT * FROM match_results')
    rows = cursor.fetchall()
    print('Database contents:')
    for row in rows:
        print(f'Team 1: {row[0]}, Team 2: {row[1]}, Goals Team 1: {row[2]}, Goals Team 2: {row[3]}')
        print(f'Team 1 Stats: {row[4]}')
        print(f'Team 2 Stats: {row[5]}')
        print('-' * 50)
except sqlite3.Error as e:
    print(f"Error while retrieving data: {e}")

# Zamknięcie bazy danych
conn.close()

# Zamknięcie przeglądarki
driver.quit()
