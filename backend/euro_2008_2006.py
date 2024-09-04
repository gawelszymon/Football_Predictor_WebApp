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
    penalty_score TEXT
)
''')

# Przetwarzanie meczów z ograniczeniem do 64
for match in matches:
    if match_count >= 64:
        break

    # Pobieranie nazw drużyn
    home_team = clean_team_name(match.find('div', class_='event__homeParticipant').get_text(strip=True))
    away_team = clean_team_name(match.find('div', class_='event__awayParticipant').get_text(strip=True))

    # Pobieranie wyniku meczu
    home_score = match.find('div', class_='event__score--home').get_text(strip=True)
    away_score = match.find('div', class_='event__score--away').get_text(strip=True)

    # Pobieranie linku do szczegółów meczu
    match_link = match.find('a', class_='eventRowLink')['href']

    # Tworzenie URL do szczegółów meczu
    detail_url = f"https://www.flashscore.pl{match_link}#/szczegoly-meczu/szczegoly-meczu"
    driver.get(detail_url)
    time.sleep(5)  # Czekanie na załadowanie strony ze szczegółami meczu

    # Pobranie źródła strony ze szczegółami
    detail_page_source = driver.page_source

    # Analiza HTML przy użyciu BeautifulSoup
    detail_soup = BeautifulSoup(detail_page_source, 'html.parser')

    # Szukanie sekcji z rzutami karnymi
    penalty_section = detail_soup.find('div', class_='smv__incidentsHeader section__title')

    penalty_score = None
    if penalty_section and 'Rzuty karne' in penalty_section.get_text():
        penalty_score = penalty_section.find_all('div')[1].text.strip()
        print(f'Penalty Score: {penalty_score}')

    # Zapisywanie wyników do bazy danych
    try:
        cursor.execute('''
        INSERT INTO match_results (
            team_id1, team_id2, goals_team_id1, goals_team_id2, penalty_score
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            home_team, away_team, home_score, away_score, penalty_score
        ))

        # Potwierdzenie zapisu
        print(f'Data saved: {home_team} {home_score} - {away_team} {away_score}')
        if penalty_score:
            print(f'Penalty Score: {penalty_score}')
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
        if row[4]:
            print(f'Penalty Score: {row[4]}')
        print('-' * 50)
except sqlite3.Error as e:
    print(f"Error while retrieving data: {e}")

# Zamknięcie bazy danych
conn.close()

# Zamknięcie przeglądarki
driver.quit()
