import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_league_rating(league, country):
    country_name = country.lower()
    league_url = "https://www.sofascore.com/api/v1/rankings/season/2024/type/1"
    response = requests.get(league_url)
    league_rating = None
    if response.status_code == 200:
        data = response.json()
        for ranking in data['rankings']:
            if ranking['uniqueTournament']['name'] == league and ranking['uniqueTournament']['category']['name'].lower() == country_name:
                league_rating = ranking['points']
    return league_rating

#Funkcja która scrappuje dane jednego zawodnika
def get_player_info(player_url):
    response = requests.get(player_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        #znalezienie imienia i nazwiska
        name_h2 = soup.find('h2', class_='Text kNUoYk')
        name = name_h2.get_text(strip=True)

        # znalezienie danych zawodnika:
        elements = soup.find_all('div', class_='Text beCNLk')
        height = None
        age = None
        for element in elements:
            if 'cm' in element.text:
                height = element.text
            elif 'lat' in element.text:
                age = element.text

        #pozycja zawodnika
        position_label = soup.find('div', string='Pozycja')
        position = None
        if position_label:
            position_div = position_label.find_next_sibling('div', class_='Text beCNLk')
            position = position_div.get_text(strip=True) if position_div else None

        #liga rozgrywkowa
        league_a = soup.find('a', href=lambda x: x and '/turniej/pilka-nozna/' in x)
        league = league_a.get_text(strip=True) if league_a else None

        #kraj ligi rozgrywkowej
        country_element = soup.find('a', href=lambda x: x and '/pl/pilka-nozna/' in x)
        if country_element:
            href = country_element['href']
            country_name = href.split('/')[-1]






    return name, height, age, league, country_name, position


# Funkcja iterująca po wszystkich zawodnikach drużyny i zbierająca ich wszystkie informacje
def get_players_info(team, tab):
    url = f"https://www.sofascore.com/pl/druzyna/pilka-nozna/{team}/{tab}#tab:squad"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        players_links = soup.find_all('a', href=True)

        hrefs = []

        for link in players_links:
            href = link['href']
            if '/pl/zawodnik/' in href and "https://www.sofascore.com" + href not in hrefs:
                hrefs.append("https://www.sofascore.com" + href)

        for href in hrefs:
            name, height, age, league, league_country, position = get_player_info(href)
            print(f"name: {name},  height: {height}, age: {age}, liga: {league}, team: {team},"
                  f" league country: {league_country},league rating: {get_league_rating(league,league_country)}, position: {position}")

    else:
        print(f"Nie znaleziono danych dla drużyny: {team}")

# # Wywołanie funkcji dla różnych drużyn
# get_players_info("germany", 4711)
# print("--------------------------------------------")
# get_players_info("poland", 4703)
# print("--------------------------------------------")
# get_players_info("scotland", 4695)
# print("--------------------------------------------")
get_players_info("switzerland", 4699)
# print("--------------------------------------------")
# print(get_league_rating("Campionato Sammarinese", "San Marino"))
# print(get_player_info("https://www.sofascore.com/pl/zawodnik/marko-arnautovic/21927"))
