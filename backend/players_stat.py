import requests
from bs4 import BeautifulSoup

def get_player_info(player_url):
    response = requests.get(player_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        #znalezienie nazwy
        name_h2 = soup.find('h2', class_='Text gcxwef')

        # Znalezienie wzrostu zawodnika
        height_label = soup.find('div', string='Wzrost')
        height = None
        if height_label:
            height_div = height_label.find_next_sibling('div', class_='Text hnfikr')
            height = height_div.get_text(strip=True) if height_div else None



        #liga rozgrywkowa
        league_a = soup.find('a', href=lambda x: x and '/turniej/pilka-nozna/' in x)
        league = league_a.get_text(strip=True) if league_a else None

        #znalezienie ratingu zawodnika

        rating_url = "https://www.sofascore.com/api/v1/player/1019322/unique-tournament/35/season/52608/statistics/overall"
        response = requests.get(rating_url)
        if response.status_code == 200:
            data = response.json()
            player_rating = data['statistics']['rating']
            goals = data['statistics']['goals']
            assists = data['statistics']['assists']
            #scrappuja sie losowe wartosci lol
    return name_h2.get_text(strip=True), player_rating, height,  league, goals, assists


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
            name, rating, height, league, goals, assists = get_player_info(href)
            print(f"name: {name}, rating: {rating}, height: {height}, liga: {league}, goals: {goals}, assists: {assists}")

    else:
        print(f"Nie znaleziono danych dla drużyny: {team}")

# Wywołanie funkcji dla różnych drużyn
get_players_info("germany", 4711)
print("--------------------------------------------")
get_players_info("hungary", 4709)
print("--------------------------------------------")
get_players_info("scotland", 4695)
print("--------------------------------------------")
get_players_info("switzerland", 4699)
print("--------------------------------------------")
