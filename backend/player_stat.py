import requests

def get_player_stat(player_id):
    stat_url = f"https://www.sofascore.com/api/v1/player/{player_id}/statistics/seasons"
    response = requests.get(stat_url)
    data = response.json()

    tournament_id = None
    latest_season_id = None
    latest_season_year = 0

    for tournament in data.get('uniqueTournamentSeasons', []):
        if 'id' in tournament['uniqueTournament']:
            tournament_id = tournament['uniqueTournament']['id']
            for season in tournament.get('seasons', []):
                season_year = int(season['year'].split('/')[0])
                if season_year > latest_season_year:
                    latest_season_year = season_year
                    latest_season_id = season['id']
            break

    return tournament_id, latest_season_id

def get_player_overall_stats(player_id, tournament_id, season_id):
    stats_url = f"https://www.sofascore.com/api/v1/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
    response = requests.get(stats_url)
    data = response.json()

    statistics = data['statistics']
    goals = statistics.get('goals', 0)
    assists = statistics.get('assists', 0)
    matches = statistics.get('matchesStarted', 0)

    return {
        'goals': goals,
        'assists': assists,
        'matches': matches
    }

player_id = 558738
tournament_id, latest_season_id = get_player_stat(player_id)
player_stats = get_player_overall_stats(player_id, tournament_id, latest_season_id)

print(player_stats)
