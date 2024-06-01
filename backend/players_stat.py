import requests
from bs4 import BeautifulSoup
from lxml import html



def get_player_rating(player_url):
    response = requests.get(player_url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        # Użycie XPath do znalezienia ratingu zawodnika
        rating = tree.xpath('/html/body/div[1]/main/div[2]/div/div/div[2]/div[1]/div[2]/div/div/span/div/span')
        if rating:
            return rating[0].strip()
    return None

def get_players_href(team, tab):
    url = f"https://www.sofascore.com/pl/druzyna/pilka-nozna/{team}/{tab}#tab:squad"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        players_links = soup.find_all('a', href=True)

        hrefs = []

        for link in players_links:
            href = link['href']
            if '/pl/zawodnik/' in href:
                hrefs.append("https://www.sofascore.com" + href)

        for href in hrefs:
            rating = get_player_rating(href)
            print(f"URL: {href}, Rating: {rating}")

    else:
        print(f"Nie znaleziono danych dla drużyny: {team}")

# Wywołanie funkcji dla różnych drużyn
# narazie cos rating nie dziala
get_players_href("germany", 4711)
print("--------------------------------------------")
get_players_href("hungary", 4709)
print("--------------------------------------------")
get_players_href("scotland", 4695)
print("--------------------------------------------")
get_players_href("switzerland", 4699)
print("--------------------------------------------")
