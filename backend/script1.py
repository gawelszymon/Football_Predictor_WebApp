import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_player_stats(session, player_id, year):
    url = f"https://www.transfermarkt.com/robert-lewandowski/leistungsdatendetails/spieler/{player_id}/plus/0?saison={year}&verein=&liga=&wettbewerb=&pos=&trainer_id="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.transfermarkt.com/robert-lewandowski/leistungsdatendetails/spieler/{player_id}/"
    }

    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.text()
                soup = BeautifulSoup(data, 'html.parser')

                # Użycie selektora CSS do znalezienia pozycji zawodnika
                position_element = soup.select_one("#tm-main > header > div.data-header__info-box > div > ul:nth-child(2) > li:nth-child(2) > span")
                position = position_element.text.strip() if position_element else "Unknown"

                # Sprawdzenie, czy zawodnik jest bramkarzem
                is_goalkeeper = "Goalkeeper" in position

                tfoot = soup.find('tfoot')
                if tfoot:
                    stats_table = tfoot.find_all('td')
                    print(f"Debug: stats_table for player {player_id} - {stats_table}")
                    print(f"Debug: stats_table length for player {player_id} - {len(stats_table)}")

                    # Wyciąganie statystyk dla bramkarzy
                    appearances = stats_table[3].text.strip() or '0'
                    yellow_red_cards = stats_table[5].text.strip().split('/')
                    yellow_cards = yellow_red_cards[0].strip() or '0'
                    red_cards = yellow_red_cards[2].strip() or '0'
                    conceded_goals = stats_table[6].text.strip() or '0'
                    clean_sheets = stats_table[7].text.strip() or '0'
                    minutes_played = stats_table[8].text.strip().replace(".", "").replace("'", "") or '0'

                    # Tworzenie słownika wyników
                    stats = {
                        "appearances": appearances,
                        "goals": '-',  # Puste dla bramkarza
                        "assists": '-',  # Puste dla bramkarza
                        "yellow_cards": yellow_cards,
                        "red_cards": red_cards,
                        "clean_sheets": clean_sheets,  # Czyste konta
                        "conceded_goals": conceded_goals,  # Stracone bramki
                        "minutes_played": minutes_played,
                        "position": position
                    }

                    print(f"Debug: Parsed stats for player {player_id} - {stats}")
                    return stats

                else:
                    print(f"No stats found in tfoot for player ID {player_id}.")
                    return None
            else:
                print(f"Failed to retrieve data for player ID {player_id}. Status code: {response.status}")
                return None
    except Exception as e:
        print(f"An error occurred while processing player ID {player_id}: {e}")
        return None

async def main():
    player_id = 44058  # Transfermarkt ID Wojciecha Szczęsnego
    year = 2021  # Rok sezonu, dla którego chcesz pobrać statystyki

    async with aiohttp.ClientSession() as session:
        stats = await fetch_player_stats(session, player_id, year)
        print(f"Statystyki dla ID zawodnika {player_id}: {stats}")

# Uruchomienie głównej funkcji
asyncio.run(main())
