import requests
import json

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
    url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/56953/standings/total"
    response = requests.get(url)
    data = response.json()
    standings = data.get('standings', [])
    all_groups = []

    for group in standings:
        group_name = group['tournament']['name']
        for row in group.get('rows', []):
            team_name = row['team']['name']
            all_groups.append({'group': group_name, 'team': team_name})

    # Convert the list of dictionaries to JSON format
    return json.dumps(all_groups, ensure_ascii=False, indent=4)



teams = get_teams_info()
print(teams)