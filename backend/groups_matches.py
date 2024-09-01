import requests
from datetime import datetime

def fetch_matches(url, group_name):
    response = requests.get(url)
    data = response.json()

    matches = []

    for event in data['events']:
        if 'groupName' in event['tournament'] and event['tournament']['groupName'] == group_name:
            date = datetime.fromtimestamp(event['startTimestamp']).strftime('%d/%m/%y %H:%M')

            if event['status']['type'] == 'notstarted':
                score = '0:0'
            else:
                home_score = event['homeScore']['current']
                away_score = event['awayScore']['current']
                score = f'{home_score} - {away_score}'

            match_info = f"{event['homeTeam']['name']} - {event['awayTeam']['name']} {date} ({score})"
            matches.append(match_info)

    return matches

api_urls = [
    'https://www.sofascore.com/api/v1/unique-tournament/1/season/56953/team-events/total',
]

group_name = 'Group B'

all_matches = []

for api_url in api_urls:
    matches = fetch_matches(api_url, group_name)
    all_matches.extend(matches)

all_matches = list(set(all_matches))

for match in all_matches:
    print(match)
