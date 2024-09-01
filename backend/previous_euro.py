import requests
import datetime

url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/26542/team-events/total"

group_map = {
    "A": ["italy", "switzerland", "turkey", "wales"],
    "B": ["belgium", "denmark", "finland", "russia"],
    "C": ["austria", "netherlands", "north macedonia", "ukraine"],
    "D": ["croatia", "czech republic", "england", "scotland"],
    "E": ["poland", "slovakia", "spain", "sweden"],
    "F": ["france", "germany", "hungary", "portugal"]
}

# url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/11098/team-events/total"
# group_map = {
#     "A": ["france", "romania", "albania", "switzerland"],
#     "B": ["england", "russia", "wales", "slovakia"],
#     "C": ["germany", "ukraine", "poland", "northern ireland"],
#     "D": ["spain", "czech republic", "turkey", "croatia"],
#     "E": ["belgium", "italy", "ireland", "sweden"],
#     "F": ["portugal", "iceland", "austria", "hungary"]
# }

team_rankings = {
    "belgium": {"rank": 1, "points": 1780},
    "france": {"rank": 2, "points": 1755},
    "england": {"rank": 4, "points": 1670},
    "portugal": {"rank": 5, "points": 1662},
    "spain": {"rank": 6, "points": 1645},
    "italy": {"rank": 10, "points": 1625},
    "croatia": {"rank": 11, "points": 1617},
    "denmark": {"rank": 12, "points": 1614},
    "germany": {"rank": 13, "points": 1610},
    "netherlands": {"rank": 14, "points": 1609},
    "switzerland": {"rank": 16, "points": 1593},
    "wales": {"rank": 18, "points": 1562},
    "poland": {"rank": 19, "points": 1559},
    "sweden": {"rank": 20, "points": 1558},
    "austria": {"rank": 23, "points": 1531},
    "ukraine": {"rank": 24, "points": 1521},
    "turkey": {"rank": 32, "points": 1487},
    "slovakia": {"rank": 34, "points": 1478},
    "russia": {"rank": 39, "points": 1461},
    "hungary": {"rank": 40, "points": 1460},
    "czech republic": {"rank": 42, "points": 1456},
    "scotland": {"rank": 48, "points": 1436},
    "finland": {"rank": 55, "points": 1411},
    "north macedonia": {"rank": 65, "points": 1362}
}

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    seen_matches = set()
    results = []
    group_standings = {group: {} for group in group_map.keys()}

    def find_matches_and_scores(obj):
        if isinstance(obj, dict):
            if 'homeTeam' in obj and 'awayTeam' in obj:
                home_team = obj.get('homeTeam', {}).get('name', '').lower()
                away_team = obj.get('awayTeam', {}).get('name', '').lower()
                home_score = obj.get('homeScore', {}).get('current')
                away_score = obj.get('awayScore', {}).get('current')
                start_timestamp = obj.get('startTimestamp')

                match_key = tuple(sorted([home_team, away_team]))
                if match_key not in seen_matches:
                    seen_matches.add(match_key)
                    for group, team_list in group_map.items():
                        if home_team in team_list and away_team in team_list:
                            match_date = datetime.datetime.fromtimestamp(start_timestamp).strftime('%d/%m/%Y %H:%M')
                            results.append({
                                "group": group,
                                "home_team": home_team.title(),
                                "away_team": away_team.title(),
                                "home_score": home_score,
                                "away_score": away_score,
                                "match_date": match_date
                            })

                            if home_team not in group_standings[group]:
                                group_standings[group][home_team] = {"points": 0, "goal_difference": 0, "goals_scored": 0}
                            if away_team not in group_standings[group]:
                                group_standings[group][away_team] = {"points": 0, "goal_difference": 0, "goals_scored": 0}

                            if home_score > away_score:
                                group_standings[group][home_team]["points"] += 3
                            elif home_score < away_score:
                                group_standings[group][away_team]["points"] += 3
                            else:
                                group_standings[group][home_team]["points"] += 1
                                group_standings[group][away_team]["points"] += 1

                            group_standings[group][home_team]["goal_difference"] += home_score - away_score
                            group_standings[group][away_team]["goal_difference"] += away_score - home_score
                            group_standings[group][home_team]["goals_scored"] += home_score
            else:
                for value in obj.values():
                    find_matches_and_scores(value)
        elif isinstance(obj, list):
            for item in obj:
                find_matches_and_scores(item)

    find_matches_and_scores(data)

    grouped_results = {group: [] for group in group_map.keys()}

    for match in results:
        grouped_results[match["group"]].append(match)

    for group in grouped_results:
        grouped_results[group].sort(key=lambda x: x["match_date"])

    for group, results in grouped_results.items():
        print(f"Grupa {group}:")
        for result in results:
            print(f" {result['home_team']} {result['home_score']} - {result['away_team']} {result['away_score']} (Data: {result['match_date']})")

    for group, standings in group_standings.items():
        print(f"\nTabela końcowa Grupa {group}:")
        sorted_standings = sorted(standings.items(), key=lambda x: (x[1]['points'], x[1]['goal_difference']), reverse=True)
        for team, stats in sorted_standings:
            rank_info = team_rankings.get(team.lower(), {"rank": "Brak", "points": "Brak"})
            print(f" {team.title()}: {stats['points']} pkt, Różnica bramek: {stats['goal_difference']}, Ranking UEFA: {rank_info['rank']} ({rank_info['points']} pkt)")
else:
    print(f"Nie udało się pobrać danych, status kod: {response.status_code}")
