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

def get_player_stat(player_id):
    stat_url = f"https://www.sofascore.com/api/v1/player/{player_id}/statistics/seasons"
    response = requests.get(stat_url)
    data = response.json()

    tournament_id = None
    latest_season_id = None
    latest_season_year = 0

    # Przeszukujemy wszystkie turnieje i pobieramy id turnieju oraz najnowszego sezonu
    for tournament in data.get('uniqueTournamentSeasons', []):
        if 'id' in tournament['uniqueTournament']:
            tournament_id = tournament['uniqueTournament']['id']
            for season in tournament.get('seasons', []):
                season_year = int(season['year'].split('/')[0])
                if season_year > latest_season_year:
                    latest_season_year = season_year
                    latest_season_id = season['id']
            break

    return tournament_id, latest_season_id

def get_player_overall_stats(player_id, tournament_id, season_id):
    stats_url = f"https://www.sofascore.com/api/v1/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
    response = requests.get(stats_url)
    data = response.json()

    statistics = data['statistics']
    goals = statistics.get('goals', 0)
    assists = statistics.get('assists', 0)
    matches = statistics.get('matchesStarted', 0)
    bigchances = statistics.get('bigChancesCreated', 0)
    keypasses = statistics.get('keyPasses', 0)
    saves = statistics.get('saves', 0)
    tackleswon = statistics.get('tacklesWon', 0)
    successfuldribbles = statistics.get('successfulDribbles', 0)
    clearances = statistics.get('clearances', 0)

    return {
        'goals': goals,
        'assists': assists,
        'matches': matches,
        'bigChancesCreated': bigchances,
        'keyPasses': keypasses,
        'saves': saves,
        'tacklesWon': tackleswon,
        'successfulDribbles': successfuldribbles,
        'clearances': clearances,

    }

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
        tournament_id, latest_season_id = get_player_stat(player_id)
        stats = get_player_overall_stats(player_id, tournament_id, latest_season_id)

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
