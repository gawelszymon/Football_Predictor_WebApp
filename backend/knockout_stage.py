import requests
import datetime

url = "https://www.sofascore.com/api/v1/unique-tournament/1/season/26542/events/last/0"
#euro 2016
#url = 'https://www.sofascore.com/api/v1/unique-tournament/1/season/11098/events/last/0'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    round_of_16_results = []
    quarterfinals_results = []
    semifinals_results = []
    final_results = []


    def find_knockout_matches_by_round(obj):
        if isinstance(obj, dict):
            if 'roundInfo' in obj:
                round_slug = obj['roundInfo'].get('slug')

                if round_slug == "round-of-16":
                    results_list = round_of_16_results
                elif round_slug == "quarterfinals":
                    results_list = quarterfinals_results
                elif round_slug == 'semifinals':
                    results_list = semifinals_results
                elif round_slug == 'final':
                    results_list = final_results
                else:
                    results_list = None

                if results_list is not None:
                    home_team = obj.get('homeTeam', {}).get('name', '').title()
                    away_team = obj.get('awayTeam', {}).get('name', '').title()
                    home_score = obj.get('homeScore', {}).get('current')
                    away_score = obj.get('awayScore', {}).get('current')
                    start_timestamp = obj.get('startTimestamp')
                    match_date = datetime.datetime.fromtimestamp(start_timestamp).strftime('%d/%m/%Y %H:%M')

                    home_score_extra_time = obj.get('homeScore', {}).get('extraTime')
                    away_score_extra_time = obj.get('awayScore', {}).get('extraTime')

                    home_score_penalty = obj.get('homeScore', {}).get('penalties')
                    away_score_penalty = obj.get('awayScore', {}).get('penalties')

                    results_list.append({
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_score": home_score,
                        "away_score": away_score,
                        "match_date": match_date,
                        "home_score_extra_time": home_score_extra_time,
                        "away_score_extra_time": away_score_extra_time,
                        "home_score_penalty": home_score_penalty,
                        "away_score_penalty": away_score_penalty
                    })
            else:
                for value in obj.values():
                    find_knockout_matches_by_round(value)
        elif isinstance(obj, list):
            for item in obj:
                find_knockout_matches_by_round(item)


    find_knockout_matches_by_round(data)

    if round_of_16_results:
        print("Wyniki fazy pucharowej - Round of 16:")
        for match in round_of_16_results:
            print(
                f"{match['home_team']} {match['home_score']} - {match['away_team']} {match['away_score']} (Data: {match['match_date']})")
            if match['home_score_extra_time'] is not None or match['away_score_extra_time'] is not None:
                print(
                    f"  * Wynik po dogrywce: {match['home_team']} {match['home_score_extra_time']} - {match['away_team']} {match['away_score_extra_time']}")
            if match['home_score_penalty'] is not None or match['away_score_penalty'] is not None:
                print(
                    f"  * Wynik po rzutach karnych: {match['home_team']} {match['home_score_penalty']} - {match['away_team']} {match['away_score_penalty']}")
    else:
        print("Brak wyników dla 'Round of 16'.")

    if quarterfinals_results:
        print("\nWyniki fazy pucharowej - Quarterfinals:")
        for match in quarterfinals_results:
            print(
                f"{match['home_team']} {match['home_score']} - {match['away_team']} {match['away_score']} (Data: {match['match_date']})")
            if match['home_score_extra_time'] is not None or match['away_score_extra_time'] is not None:
                print(
                    f"  * Wynik po dogrywce: {match['home_team']} {match['home_score_extra_time']} - {match['away_team']} {match['away_score_extra_time']}")
            if match['home_score_penalty'] is not None or match['away_score_penalty'] is not None:
                print(
                    f"  * Wynik po rzutach karnych: {match['home_team']} {match['home_score_penalty']} - {match['away_team']} {match['away_score_penalty']}")
    else:
        print("Brak wyników dla 'Quarterfinals'.")

    if semifinals_results:
        print("\nWyniki fazy pucharowej - Semifinals:")
        for match in semifinals_results:
            print(
                f"{match['home_team']} {match['home_score']} - {match['away_team']} {match['away_score']} (Data: {match['match_date']})")
            if match['home_score_extra_time'] is not None or match['away_score_extra_time'] is not None:
                print(
                    f"  * Wynik po dogrywce: {match['home_team']} {match['home_score_extra_time']} - {match['away_team']} {match['away_score_extra_time']}")
            if match['home_score_penalty'] is not None or match['away_score_penalty'] is not None:
                print(
                    f"  * Wynik po rzutach karnych: {match['home_team']} {match['home_score_penalty']} - {match['away_team']} {match['away_score_penalty']}")
    else:
        print("Brak wyników dla 'Semifinals'.")

    if final_results:
        print("\nWyniki fazy pucharowej - Final:")
        for match in final_results:
            print(
                f"{match['home_team']} {match['home_score']} - {match['away_team']} {match['away_score']} (Data: {match['match_date']})")
            if match['home_score_extra_time'] is not None or match['away_score_extra_time'] is not None:
                print(
                    f"  * Wynik po dogrywce: {match['home_team']} {match['home_score_extra_time']} - {match['away_team']} {match['away_score_extra_time']}")
            if match['home_score_penalty'] is not None or match['away_score_penalty'] is not None:
                print(
                    f"  * Wynik po rzutach karnych: {match['home_team']} {match['home_score_penalty']} - {match['away_team']} {match['away_score_penalty']}")
    else:
        print("Brak wyników dla 'Final'.")
else:
    print(f"Nie udało się pobrać danych, status kod: {response.status_code}")