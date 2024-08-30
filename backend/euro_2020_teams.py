import requests
from bs4 import BeautifulSoup
import unidecode

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

url = "https://www.transfermarkt.pl/europameisterschaft-2012/gesamtspielplan/pokalwettbewerb/EM12/saison_id/2011"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    table_rows = soup.select("table tbody tr")

    matches = []

    for row in table_rows:
        cells = row.find_all('td')
        if len(cells) >= 8:
            team1_anchor = cells[3].find('a')
            team2_anchor = cells[7].find('a')

            if team1_anchor and team2_anchor:
                team1 = team1_anchor.text.strip()
                team1 = unidecode.unidecode(team1)
                team1_id = team1_anchor['href'].split('/')[-3]

                result_link = cells[5].find('a')
                result = result_link.text if result_link else 'No Result'
                match_id = result_link['href'].split('/')[-1] if result_link else 'No Match ID'

                team2 = team2_anchor.text.strip()
                team2 = unidecode.unidecode(team2)
                team2_id = team2_anchor['href'].split('/')[-3]

                team1_url_part = unidecode.unidecode(team1.replace(' ', '_').lower())
                team2_url_part = unidecode.unidecode(team2.replace(' ', '_').lower())

                if "No Result" not in result:
                    matches.append({
                        "team1": team1,
                        "team1_url_part": team1_url_part,
                        "team1_id": team1_id,
                        "result": result,
                        "team2": team2,
                        "team2_url_part": team2_url_part,
                        "team2_id": team2_id,
                        "match_id": match_id,
                    })

    for match in matches:
        print(f"Match ID: {match['match_id']} | {match['team1']} (ID: {match['team1_id']}) {match['result']} {match['team2']} (ID: {match['team2_id']})")

        match_url = f"https://www.transfermarkt.pl/{match['team1_url_part']}_{match['team2_url_part']}/statistik/spielbericht/{match['match_id']}"

        match_response = requests.get(match_url, headers=headers)
        match_soup = BeautifulSoup(match_response.content, "html.parser")

        stat_sections = match_soup.find_all("div", class_="sb-statistik")

        for stat_section in stat_sections:
            stat_title = stat_section.find_previous_sibling("div", class_="unterueberschrift").text.strip()

            stat_values = stat_section.find_all("div", class_="sb-statistik-zahl")
            if len(stat_values) >= 2:
                home_stat = unidecode.unidecode(stat_values[0].text.strip())  # Convert Polish characters
                away_stat = unidecode.unidecode(stat_values[1].text.strip())  # Convert Polish characters
                print(f"{stat_title}: {home_stat} - {away_stat}")
            else:
                print(f"{stat_title}: Brak pelnych danych statystycznych.")
        print("\n")

else:
    print("Failed to retrieve the page")
