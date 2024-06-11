import requests

def get_team_matches(team_name, team_id):
    team_url = f"https://www.sofascore.com/api/v1/team/{team_id}/events/last/0"

    response = requests.get(team_url)
    data = response.json()

    matches = [
        (match['customId'], match['id'], match['homeTeam']['name'], match['awayTeam']['name'], match['startTimestamp'], match['tournament']['name'])
        for match in data['events']
    ]

    matches.sort(key=lambda x: x[4], reverse=True)

    last_10_matches = matches[:10]

    for custom_id, match_id, home_team, away_team, match_date, match_type in last_10_matches:
        incidents_url = f"https://www.sofascore.com/api/v1/event/{match_id}/incidents"

        incidents_response = requests.get(incidents_url)
        incidents_data = incidents_response.json()

        home_score = away_score = "N/A"
        scorers = []
        assists = []
        man_of_the_match = None

        for incident in incidents_data['incidents']:
            if incident.get('incidentType') == 'period' and incident.get('text') == 'FT':
                home_score = incident['homeScore']
                away_score = incident['awayScore']
            elif incident.get('incidentType') == 'goal':
                scorer = incident.get('player', {}).get('name', 'Unknown')
                assist = incident.get('assist1', {}).get('name', None)
                scorers.append(scorer)
                if assist:
                    assists.append(assist)
            elif incident.get('incidentType') == 'manOfTheMatch':
                man_of_the_match = incident.get('player', {}).get('name', 'Unknown')

        if home_score == "N/A" or away_score == "N/A":
            result = "N/A"
        elif (home_team == team_name and home_score > away_score) or (away_team == team_name and away_score > home_score):
            result = "W"
        elif home_score == away_score:
            result = "D"
        else:
            result = "L"

        print(f"Match: {home_team}-{away_team}, Score: {home_score}-{away_score}, Result: {result}, Type: {match_type}")
        print(f"Scorers: {', '.join(scorers)}")
        print(f"Assists: {', '.join(assists)}")
        if man_of_the_match:
            print(f"Man of the Match: {man_of_the_match}")

get_team_matches("Poland", 4703)
