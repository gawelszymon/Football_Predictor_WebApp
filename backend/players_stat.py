import requests
from bs4 import BeautifulSoup
from script import create_database

def get_league_rating(league, country):
    country_name = country.lower()
    league_url = "https://www.sofascore.com/api/v1/rankings/season/2024/type/1"
    response = requests.get(league_url)
    league_rating = None
    if response.status_code == 200:
        data = response.json()
        for ranking in data['rankings']:
            if ranking['uniqueTournament']['name'] == league and ranking['uniqueTournament']['category'][
                'name'].lower() == country_name:
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
    season_id = None

    for tournament in data.get('uniqueTournamentSeasons', []):
        if 'id' in tournament['uniqueTournament']:
            for season in tournament.get('seasons', []):
                if ("23/24" in season['name'] and season['year'] == "23/24") or (
                        season['year'] == "2024" and "MLS" in season['name']):
                    tournament_id = tournament['uniqueTournament']['id']
                    season_id = season['id']
                    break
        if season_id:
            break

    return tournament_id, season_id


def check_player_in_database(conn, name):
    cursor = conn.cursor()

    # Wykonaj zapytanie, aby sprawdzić, czy imię istnieje w bazie danych
    cursor.execute("SELECT COUNT(*) FROM players WHERE player_name=?", (name,))
    result = cursor.fetchone()

    # Zwróć True, jeśli imię istnieje w bazie danych, w przeciwnym razie False
    return result[0] > 0


# Funkcja, która scrappuje dane jednego zawodnika
def get_player_info(conn, player_url):
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
                h = element.text
                height = h.split(' ')[0]

            elif 'lat' in element.text:
                a = element.text
                age = a.split(' ')[0]

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

        goals = stats['goals']
        assists = stats['assists']
        matches = stats['matches']
        bigchances = stats['bigChancesCreated']
        keyPasses = stats['keyPasses']
        saves = stats['saves']
        tackleswon = stats['tacklesWon']
        successfulDribbles = stats['successfulDribbles']
        clearances = stats['clearances']

        if check_player_in_database(conn, name):
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players
                SET height = ?, age = ?, league = ?, pos = ?, rating = ?, goals = ?, assists = ?, matches = ?, bigchances = ?, keyPasses = ?, saves = ?, tackleswon = ?, successfulDribbles = ?, clearances = ?
                WHERE player_name = ?
            ''', (
            height, age, league, position, rating, goals, assists, matches, bigchances, keyPasses, saves,
            tackleswon, successfulDribbles, clearances, name))
            conn.commit()
            print(f"Updated player {name} in the database.")
        else:
            print(f"Player {name} does not exist in the database.")

        return name, height, age, league, country_name, position, rating, goals, assists, matches, bigchances, keyPasses, saves, tackleswon, successfulDribbles, clearances


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
    tournament = "euro"
    conn = create_database(tournament, 2024)

    hrefs = get_players_hrefs(team, tab)

    for href in hrefs:
        try:
            name, height, age, league, league_country, position, rating, goals, assists, matches, bigchances, keyPasses, saves, tackleswon, successfulDribbles, clearances = get_player_info(
                conn, href)
            league_rating = get_league_rating(league, league_country) if league and league_country else "Brak danych"
            print(f"Name: {name}, Height: {height}, Age: {age}, League: {league}, League Country: {league_country}, "
                  f"League Rating: {league_rating}, Position: {position}, Player Rating: {rating}, Goals: {goals}, assists: {assists}, matches: {matches}, bigchances: {bigchances}"
                  f"keyPasses: {keyPasses}, saves: {saves}, tackleswon: {tackleswon}, successfulDribbles: {successfulDribbles}, clearances: {clearances}")
        except Exception as e:
            print(f"Nie udało się pobrać danych dla zawodnika z URL: {href}. Błąd: {e}")

    conn.close()


# Wywołanie funkcji dla różnych drużyn
get_players_info("switzerland", 4699)
get_players_info("hungary", 4709)
get_players_info("scotland", 4695)
get_players_info("spain", 4698)
get_players_info("italy", 4707)
get_players_info("albania", 4690)
get_players_info("croatia", 4715)
get_players_info("england", 4713)
get_players_info("denmark", 4476)
get_players_info("slovenia", 4484)
get_players_info("serbia", 6355)
get_players_info("netherlands", 4705)
get_players_info("france", 4481)
get_players_info("poland", 4703)
get_players_info("germany", 4711)
get_players_info("austria", 4718)
get_players_info("romania", 4477)
get_players_info("slovakia", 4697)
get_players_info("belgium", 4717)
get_players_info("ukraine", 4701)
get_players_info("turkey", 4700)
get_players_info("portugal", 4704)
get_players_info("czech-republic", 4714)
get_players_info("georgia", 4763)
