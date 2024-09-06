import sqlite3
import pandas as pd

# Function to load a table from a database
def load_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


# Position mapping to general categories
position_mapping = {
    'Goalkeeper': 'Goalkeeper',
    'Centre-Back': 'Defense',
    'Left-Back': 'Defense',
    'Right-Back': 'Defense',
    'Central Midfield': 'Midfield',
    'Attacking Midfield': 'Midfield',
    'Defensive Midfield': 'Midfield',
    'Right Midfield': 'Midfield',
    'Left Midfield': 'Midfield',
    'Left Winger': 'Attack',
    'Right Winger': 'Attack',
    'Centre-Forward': 'Attack',
    'Second Striker': 'Attack'
}


# Function to update or insert club stats into the database
def upsert_club_stats(cursor, team_id, general_position, stats):
    cursor.execute('''
        INSERT INTO club_stats (
            team_id, position, ranking, clean_sheets, conceded_goals, value, appearances, goals, assists, yellow_cards, red_cards, minutes_played
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(team_id, position) DO UPDATE SET 
            ranking=excluded.ranking,
            clean_sheets=excluded.clean_sheets,
            conceded_goals=excluded.conceded_goals,
            value=excluded.value,
            appearances=excluded.appearances,
            goals=excluded.goals,
            assists=excluded.assists,
            yellow_cards=excluded.yellow_cards,
            red_cards=excluded.red_cards,
            minutes_played=excluded.minutes_played
    ''', (
        team_id, general_position,
        stats.get('ranking', None), stats.get('clean_sheets', None),
        stats.get('conceded_goals', None), stats.get('value', None),
        stats.get('appearances', None), stats.get('goals', None),
        stats.get('assists', None), stats.get('yellow_cards', None),
        stats.get('red_cards', None), stats.get('minutes_played', None)
    ))


# Function to update or insert tournament stats into the database
def upsert_tournament_stats(cursor, team_id, general_position, stats):
    cursor.execute('''
        INSERT INTO tournament_stats (
            team_id, position, goals, assists, minutes, 
            yellow_cards, red_cards, starting_eleven, substituted_in, on_bench, suspended, injured, absence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(team_id, position) DO UPDATE SET 
            goals=excluded.goals,
            assists=excluded.assists,
            minutes=excluded.minutes,
            yellow_cards=excluded.yellow_cards,
            red_cards=excluded.red_cards,
            starting_eleven=excluded.starting_eleven,
            substituted_in=excluded.substituted_in,
            on_bench=excluded.on_bench,
            suspended=excluded.suspended,
            injured=excluded.injured,
            absence=excluded.absence
    ''', (
        team_id, general_position,
        stats.get('goals', None), stats.get('assists', None),
        stats.get('minutes', None), stats.get('yellow_cards', None),
        stats.get('red_cards', None), stats.get('starting_eleven', None),
        stats.get('substituted_in', None), stats.get('on_bench', None),
        stats.get('suspended', None), stats.get('injured', None),
        stats.get('absence', None)
    ))


# Function to aggregate team stats by general position and upsert into the appropriate table
def aggregate_team_stats_by_position(team_id, teams, player_stats, market_value, cursor):
    print(f"Processing team_id: {team_id}")

    # Convert team_id to int for consistency
    team_id = int(team_id)

    # Find all players in the team based on transfermarkt_id
    team_players = teams[teams['team_id'] == team_id]['transfermarkt_id']

    if team_players.empty:
        print(f"No players found for team_id {team_id}")
        return

    # Get player statistics for this tournament
    team_player_stats = player_stats[player_stats['player_id'].isin(team_players)]

    # Print available columns in the player_stats DataFrame for debugging
    print("Available columns in player_stats:", team_player_stats.columns)

    # Get market value data before the tournament
    team_market_values = market_value[market_value['player_id'].isin(team_players)]

    # Group by general position and calculate average stats for each general position
    for general_position, players_in_general_position in team_market_values.groupby(
            market_value['position'].map(position_mapping)):

        # Get player stats for this position during the tournament
        stats_for_general_position = team_player_stats[
            team_player_stats['player_id'].isin(players_in_general_position['player_id'])]

        # Handle club stats (from market_value_history)
        club_stats_for_general_position = players_in_general_position[
            ['value', 'ranking', 'clean_sheets', 'conceded_goals', 'appearances', 'goals', 'assists', 'yellow_cards',
             'red_cards', 'minutes_played']].mean().to_dict()
        upsert_club_stats(cursor, team_id, general_position, club_stats_for_general_position)

        # Handle tournament stats (from player_stats)
        if general_position == 'Goalkeeper':
            available_columns = ['clean_sheets', 'conceded_goals', 'minutes', 'yellow_cards', 'red_cards',
                                 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence']
        else:
            available_columns = ['goals', 'assists', 'minutes', 'yellow_cards', 'red_cards',
                                 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence']

        # Filter columns that exist in stats_for_position
        available_columns = [col for col in available_columns if col in stats_for_general_position.columns]

        tournament_stats_for_general_position = stats_for_general_position[available_columns].mean().to_dict()

        upsert_tournament_stats(cursor, team_id, general_position, tournament_stats_for_general_position)


# Example for processing Euro 2024
def process_euro_2024():
    conn = sqlite3.connect('euro_2012_stats.db')
    cursor = conn.cursor()

    # Create tables for club stats and tournament stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS club_stats (
            team_id INTEGER,
            position TEXT,
            ranking REAL,
            clean_sheets REAL,
            conceded_goals REAL,
            value REAL,
            appearances REAL,
            goals REAL,
            assists REAL,
            yellow_cards REAL,
            red_cards REAL,
            minutes_played REAL,
            UNIQUE(team_id, position) -- Ensure uniqueness for team_id and position
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tournament_stats (
            team_id INTEGER,
            position TEXT,
            goals REAL,
            assists REAL,
            yellow_cards REAL,
            red_cards REAL,
            minutes REAL,
            starting_eleven REAL,
            substituted_in REAL,
            on_bench REAL,
            suspended REAL,
            injured REAL,
            absence REAL,
            UNIQUE(team_id, position) -- Ensure uniqueness for team_id and position
        )
    ''')

    # Load data from databases
    matches_2024 = load_table('euro2012_matches_info.db', 'matches')
    teams_2024 = load_table('euro1_teams2012.db', 'teams')
    player_stats_2024 = load_table('euro1_teams2012.db', 'players_stats')
    market_value_2024 = load_table('euro1_teams2012.db', 'market_value_history')

    for _, match in matches_2024.iterrows():
        team1_id = match['team1_id']
        team2_id = match['team2_id']

        print(f"Processing match {team1_id} vs {team2_id}")

        # Aggregate stats for both teams
        aggregate_team_stats_by_position(team1_id, teams_2024, player_stats_2024, market_value_2024, cursor)
        aggregate_team_stats_by_position(team2_id, teams_2024, player_stats_2024, market_value_2024, cursor)

    conn.commit()
    conn.close()


# Main program execution
if __name__ == '__main__':
    process_euro_2024()
