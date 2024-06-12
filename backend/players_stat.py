import requests
from bs4 import BeautifulSoup

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

def get_player_rating(player_id):
    url = f'https://www.sofascore.com/api/v1/player/{player_id}/last-year-summary'
    response = requests.get(url)
    player_ratings = []
    if response.status_code == 200:
        data = response.json()
        for value in data['summary']:
            if value['type'] == "event":
                player_ratings.append(float(value['value']))
    rating_sum = sum(player_ratings)
    try:
        mean = rating_sum / len(player_ratings)
    except ZeroDivisionError:
        mean = None
    return mean

# Funkcja do pobierania szczegółowych statystyk zawodnika
def get_player_statistics(player_url):
    leagues = {
        'england Premier League' : [17, 52186],
        'spain LaLiga' : [8, 52376],
        'turkey Trendyol Süper Lig' : [52, 53190],
        'italy Serie A' : [23, 52760],
        'france Ligue 1' : [34, 52571],
        'poland Ekstraklasa' : [202, 61236],
        'greece Stoiximan Super League' : [185, 53223],
        'bulgaria Parva Liga' : [247, 52173],
        'usa MLS' : [524, 57317],
               }
    response = requests.get(player_url)
    if response.status_code == 200:
        # Liga rozgrywkowa
        soup = BeautifulSoup(response.content, 'html.parser')
        league_a = soup.find('a', href=lambda x: x and '/turniej/pilka-nozna/' in x)
        league = league_a.get_text(strip=True) if league_a else None

        # Kraj ligi rozgrywkowej
        country_element = soup.find('a', href=lambda x: x and '/pl/pilka-nozna/' in x)
        if country_element:
            href = country_element['href']
            country_name = href.split('/')[-1]
    print(country_name, league)
    name = country_name+ " " + league
    id1, id2 = leagues[name]

    player_id = player_url.split('/')[-1]
    url = f'https://www.sofascore.com/api/v1/player/{player_id}/unique-tournament/{id1}/season/{id2}/statistics/overall'
    response = requests.get(url)
    statistics = {}
    if response.status_code == 200:
        data = response.json()
        statistics['matches_played'] = data['statistics'].get('matchesStarted', 'N/A')
        statistics['goals'] = data['statistics'].get('goals', 'N/A')
        statistics['assists'] = data['statistics'].get('assists', 'N/A')
        statistics['shots_per_game'] = data['statistics'].get('shotsOnTarget', 'N/A')
        statistics['key_passes'] = data['statistics'].get('keyPasses', 'N/A')
        statistics['yellow_cards'] = data['statistics'].get('yellowCards', 'N/A')
        statistics['red_cards'] = data['statistics'].get('redCards', 'N/A')
    return statistics

# Funkcja, która scrappuje dane jednego zawodnika
def get_player_info(player_url):
    response = requests.get(player_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Znalezienie imienia i nazwiska
        name_h2 = soup.find('h2', class_='Text kNUoYk')
        name = name_h2.get_text(strip=True) if name_h2 else None

        # Znalezienie danych zawodnika:
        elements = soup.find_all('div', class_='Text beCNLk')
        height = None
        age = None
        for element in elements:
            if 'cm' in element.text:
                height = element.text
            elif 'lat' in element.text:
                age = element.text

        # Pozycja zawodnika
        position_label = soup.find('div', string='Pozycja')
        position = None
        if position_label:
            position_div = position_label.find_next_sibling('div', class_='Text beCNLk')
            position = position_div.get_text(strip=True) if position_div else None

        # Liga rozgrywkowa
        league_a = soup.find('a', href=lambda x: x and '/turniej/pilka-nozna/' in x)
        league = league_a.get_text(strip=True) if league_a else None

        # Kraj ligi rozgrywkowej
        country_element = soup.find('a', href=lambda x: x and '/pl/pilka-nozna/' in x)
        if country_element:
            href = country_element['href']
            country_name = href.split('/')[-1]

        # Pobranie id z linku
        player_id = player_url.split('/')[-1]

        # Rating zawodnika
        rating = get_player_rating(player_id)

        # Statystyki zawodnika
        stats = get_player_statistics(player_url)

        return name, height, age, league, country_name, position, rating, stats

def get_players_hrefs(team, tab):
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
        return hrefs
    else:
        print("Nie udało się połączyć ze stroną")
        return None

# Funkcja iterująca po wszystkich zawodnikach drużyny i zbierająca ich wszystkie informacje
def get_players_info(team, tab):
    hrefs = get_players_hrefs(team, tab)

    for href in hrefs:
        try:
            name, height, age, league, league_country, position, rating, stats = get_player_info(href)
            league_rating = get_league_rating(league, league_country) if league and league_country else "Brak danych"
            print(f"Name: {name}, Height: {height}, Age: {age}, League: {league}, League Country: {league_country}, "
                  f"League Rating: {league_rating}, Position: {position}, Player Rating: {rating}")
            print("Stats:")
            for stat_name, stat_value in stats.items():
                print(f"  {stat_name}: {stat_value}")
            print("\n")
        except Exception as e:
            print(f"Nie udało się pobrać danych dla zawodnika z URL: {href}. Błąd: {e}")

# Wywołanie funkcji dla różnych drużyn
get_players_info("poland", 4703)