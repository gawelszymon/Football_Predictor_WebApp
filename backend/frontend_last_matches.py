import requests

def get_team_matches(team_id):
    team_url = f"https://www.sofascore.com/api/v1/team/{team_id}/events/last/0"

    response = requests.get(team_url)
    data = response.json()

    matches = [
        (match['customId'], match['id'], match['homeTeam']['name'], match['awayTeam']['name'], match['startTimestamp'], match['tournament']['name'])
        for match in data['events']
    ]

    matches.sort(key=lambda x: x[4], reverse=True)

    last_3_matches = matches[:3]
    match_results = []

    for custom_id, match_id, home_team, away_team, match_date, match_type in last_3_matches:
        incidents_url = f"https://www.sofascore.com/api/v1/event/{match_id}/incidents"

        incidents_response = requests.get(incidents_url)
        incidents_data = incidents_response.json()

        home_score = away_score = "N/A"
        scorers = []
        assists = []

        for incident in incidents_data.get('incidents', []):
            if incident.get('incidentType') == 'period' and incident.get('text') == 'FT':
                home_score = incident['homeScore']
                away_score = incident['awayScore']
            elif incident.get('incidentType') == 'goal':
                scorer = incident.get('player', {}).get('name', 'Unknown')
                assist = incident.get('assist1', {}).get('name', None)
                scorers.append(scorer)
                if assist:
                    assists.append(assist)

        if home_score == "N/A" or away_score == "N/A":
            result = "N/A"
        elif home_score > away_score:
            result = "W" if home_team == data['events'][0]['homeTeam']['name'] else "L"
        elif home_score < away_score:
            result = "L" if home_team == data['events'][0]['homeTeam']['name'] else "W"
        else:
            result = "D"

        match_results.append({
            "match": f"{home_team} - {away_team}",
            "score": f"{home_score} - {away_score}",
            "result": result,
            "type": match_type,
            "scorers": scorers,
            "assists": assists
        })

    return match_results
