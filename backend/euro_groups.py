import requests
import json
import pandas as pd
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

# Tutaj bocik scrappuje info ktore pozniej bedziemy dodawac do bazy danych
def get_teams_info():
    url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/56953/standings/total"
    response = requests.get(url)
    data = response.json()
    standings = data.get('standings', [])
    all_groups = []

    ratings = get_countries_rating()

    for group in standings:
        group_name = group['tournament']['name']
        for row in group.get('rows', []):
            team_name = row['team']['name']
            points = row['points']
            rating = ratings.get(team_name, 'Brak danych')
            all_groups.append({
                'group': group_name,
                'team': team_name,
                'points': points,
                'rating': rating
            })
    return all_groups

def display_standings():
    teams_info = get_teams_info()
    if teams_info:
        df = pd.DataFrame(teams_info)
        df_sorted = df.sort_values(by=['group'])
        print(df_sorted)
    else:
        print("Nie udało się pobrać danych o zespołach.")

display_standings()