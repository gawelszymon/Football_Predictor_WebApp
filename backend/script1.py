import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

# Zakładając, że już zaimplementowałeś funkcję get_transfermarkt_id i fetch.
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

async def test_get_transfermarkt_id():
    async with aiohttp.ClientSession() as session:
        # Przetestowanie kilku różnych zawodników
        test_players = ["Lionel Messi", "Cristiano Ronaldo", "Robert Lewandowski", "Pedro Miguel", "Morteza Pouraliganji", "Ali Karimi", "Aaron Mooy", "Thomas Deng", "Carlos Martínez", "Jerome Ngom Mbekeli"]
        for player in test_players:
            player_id = await get_transfermarkt_id(session, player)
            if player_id:
                print(f"Player ID for {player} is {player_id}")
            else:
                print(f"Player ID for {player} could not be found")

# Uruchomienie testu
asyncio.run(test_get_transfermarkt_id())
