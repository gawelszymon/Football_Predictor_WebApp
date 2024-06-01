import requests
import pandas as pd

payload = {}
url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/56953/standings/total"
headers = {
    'accept': '*/*',
    'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': '_gcl_au=1.1.385624786.1717001362; _ga=GA1.1.1766192606.1717001362; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CP_YGAAP_YGAAEsACBPLA2EoAP_gAEPgAA6II3gB5C5ETSFBYH51KIsEYAEHwAAAIsAgAAYBAQABQBKQAIQCAGAAEAhAhCACgAAAIEYBIAEACAAQAAAAAAAAIAAEIAAQAAAIICAAAAAAAABIAAAIAAAAEAAAwCAABAAA0AgEAJIISMgAAAAAAAAAAgAAAAAAAgAAAEhAAAEIAAAAACgAEABAEAAAAAEIABBII3gB5C5ETSFBYHhVIIMEIAERQAAAIsAgAAQBAQAAQBKQAIQCEGAAAAgAACAAAAAAIEQBIAEAAAgAAAAAAAAAIAAEAAAAAAAIICAAAAAAAABAAAAIAAAAAAAAwCAABAAAwQhEAJIASEgAAAAgAAAAAoAAAAAAAgAAAEhAAAEAAAAAAAAAEAAAEAAAAAAAABBIAAA.dnAACAgAAAA%22%2C%222~41.70.89.108.149.211.313.358.415.486.540.621.981.1029.1046.1092.1097.1126.1205.1301.1516.1558.1584.1598.1651.1697.1716.1753.1810.1832.1985.2328.2373.2440.2571.2572.2575.2577.2628.2642.2677.2767.2860.2878.2887.2922.3182.3190.3234.3290.3292.3331.10631~dv.%22%2C%2256DA6A83-A2F1-477A-B732-CD60550E94D9%22%5D%5D; clever-last-tracker-66554=1; __gads=ID=0fc9c59f9fc4ed2d:T=1717001370:RT=1717155502:S=ALNI_Maa-5XCW295Af4J_PdsRoEo8a-GZQ; __eoi=ID=40faaf7eae8465e5:T=1717001370:RT=1717155502:S=AA-AfjZLdI7Ie1Z1ggiaNlRFpqGm; FCNEC=%5B%5B%22AKsRol_YrjlNeVLdkbda-9C4w4GvGIVYP3FELgs2-goEu-qQgBkMzKktXn6AbkCMVgEILo908rmoLOluqgk4G3EzXCWpQhCaanUHN8V7kkBz7yif1UCJknU3gahNgGLAIDxnyJUzB65RArhkfkpx0wVYO3wVeWxNjw%3D%3D%22%5D%5D; _ga_HNQ9P9MGZR=GS1.1.1717152962.5.1.1717155514.9.0.0; _ga_QH2YGS7BB4=GS1.1.1717155457.6.1.1717155515.0.0.0; _ga_3KF4XTPHC4=GS1.1.1717155457.6.1.1717155515.2.0.0',
    'if-none-match': 'W/"974e9921d1"',
    'priority': 'u=1, i',
    'referer': 'https://www.sofascore.com/pl/turniej/pilka-nozna/europe/european-championship/1',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'x-requested-with': '8b7e60'
}
def get_countries_rating():
    url = "https://www.sofascore.com/api/v1/rankings/type/2"
    response = requests.get(url)
    rating_dict = {}
    if response.status_code == 200:
        data = response.json()
        for ranking in data['rankings']:
            team_name = ranking['team']['name']
            points = ranking['points']
            rating_dict[team_name] = points
        return rating_dict
    else:
        print(f"Nie udało się pobrać danych, status code: {response.status_code}")
        return None

def get_team_points(name):
    teams_points = get_countries_rating()
    return teams_points[name]



# Tutaj bocik scrappuje info ktore pozniej bedziemy dodawac do bazy danych
def get_teams_info():
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    standings = data.get('standings', [])
    all_groups = []
    for group in standings:
        group_name = group['tournament']['name']
        for row in group.get('rows', []):
            team_name = row['team']['name']
            points = row['points']
            wins = row['points']
            losses = row['losses']
            draws = row['draws']
            team_points = get_team_points(team_name)
            all_groups.append({'group' : group_name, 'team': team_name, 'points' : points, 'wins' : wins, 'draws' : draws, 'losses' : losses, 'team_points' : team_points})

    df_all_groups = pd.DataFrame(all_groups)
    print(df_all_groups)

get_teams_info()