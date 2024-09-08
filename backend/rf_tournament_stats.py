import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

# Synchronize number_of_matches for all positions within the same team
def synchronize_number_of_matches(predicted_stats):
    # Group by team_id and calculate the maximum number of matches for each team
    max_matches_by_team = predicted_stats.groupby('team_id')['number_of_matches'].transform('max')

    # Assign the max number of matches to all positions within the same team
    predicted_stats['number_of_matches'] = max_matches_by_team
    return predicted_stats

# Function to clean and prepare data
def clean_data(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)
    return df


# Prepare data for Random Forest training
def prepare_rf_data(club_stats, tournament_stats):
    non_predictive_columns = ['team_id', 'position']
    X = clean_data(club_stats.drop(columns=non_predictive_columns))
    y = clean_data(tournament_stats.drop(columns=non_predictive_columns))
    return X, y

# Train Random Forest models with cross-validation
def train_random_forest_models(X, y, position):
    models = {}

    # Define the columns to predict based on position
    if position == 'Goalkeeper':
        columns_to_predict = ['minutes', 'yellow_cards', 'red_cards', 'starting_eleven', 'substituted_in',
                              'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches']
    else:
        columns_to_predict = ['goals', 'assists', 'minutes', 'yellow_cards', 'red_cards', 'starting_eleven',
                              'substituted_in', 'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches']

    for column in columns_to_predict:
        print(f"Training Random Forest model for {column} for position {position}...")

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y[column], test_size=0.2, random_state=0)

        rf_model = RandomForestRegressor(n_estimators=200, random_state=20)

        # Fit model on training data
        rf_model.fit(X_train, y_train)

        # Test the model
        predictions = rf_model.predict(X_test)
        predictions = np.round(predictions).astype(int)  # Ensure integer predictions
        mse = mean_squared_error(y_test, predictions)
        print(f"Test MSE for {column} ({position}): {mse}")
        models[column] = rf_model

    return models


# Predict tournament stats for Euro 2024 using trained models
def predict_rf_for_euro_2024(models, club_stats_2024):
    X_euro_2024 = clean_data(club_stats_2024.drop(columns=['team_id', 'position']))

    predictions = {}
    for column, model in models.items():
        predictions[column] = np.round(model.predict(X_euro_2024)).astype(int)  # Ensure integer predictions

    predicted_tournament_stats = pd.DataFrame(predictions)
    predicted_tournament_stats['team_id'] = club_stats_2024['team_id'].values
    predicted_tournament_stats['position'] = club_stats_2024['position'].values

    return predicted_tournament_stats


# Function to copy club_stats from euro_2024_stats.db to the new predictions database
def copy_club_stats_to_new_db(source_db_path, destination_db_path):
    source_conn = sqlite3.connect(source_db_path)
    club_stats_2024 = pd.read_sql_query("SELECT * FROM club_stats", source_conn)
    dest_conn = sqlite3.connect(destination_db_path)
    club_stats_2024.to_sql('club_stats', dest_conn, if_exists='replace', index=False)
    source_conn.close()
    dest_conn.close()

# Main workflow
def run_rf_on_combined_tournaments(tournaments, euro_2024_db_path):
    combined_X_goalkeepers = []
    combined_y_goalkeepers = []
    combined_X_field_players = []
    combined_y_field_players = []

    for tournament in tournaments:
        print(f"\nProcessing {tournament['name']}...")

        conn = sqlite3.connect(tournament['db_path'])
        club_stats = pd.read_sql_query("SELECT * FROM club_stats", conn)
        tournament_stats = pd.read_sql_query("SELECT * FROM tournament_stats", conn)
        conn.close()

        club_stats_goalkeepers = club_stats[club_stats['position'] == 'Goalkeeper']
        club_stats_field_players = club_stats[club_stats['position'] != 'Goalkeeper']

        tournament_stats_goalkeepers = tournament_stats[tournament_stats['position'] == 'Goalkeeper']
        tournament_stats_field_players = tournament_stats[tournament_stats['position'] != 'Goalkeeper']

        X_goalkeepers, y_goalkeepers = prepare_rf_data(club_stats_goalkeepers, tournament_stats_goalkeepers)
        X_field_players, y_field_players = prepare_rf_data(club_stats_field_players, tournament_stats_field_players)

        combined_X_goalkeepers.append(X_goalkeepers)
        combined_y_goalkeepers.append(y_goalkeepers)
        combined_X_field_players.append(X_field_players)
        combined_y_field_players.append(y_field_players)

    X_goalkeepers_combined = pd.concat(combined_X_goalkeepers)
    y_goalkeepers_combined = pd.concat(combined_y_goalkeepers)
    X_field_players_combined = pd.concat(combined_X_field_players)
    y_field_players_combined = pd.concat(combined_y_field_players)

    goalkeeper_models = train_random_forest_models(X_goalkeepers_combined, y_goalkeepers_combined,
                                                   position='Goalkeeper')
    field_player_models = train_random_forest_models(X_field_players_combined, y_field_players_combined,
                                                     position='Field')

    conn = sqlite3.connect(euro_2024_db_path)
    club_stats_2024 = pd.read_sql_query("SELECT * FROM club_stats", conn)
    conn.close()

    club_stats_2024_goalkeepers = club_stats_2024[club_stats_2024['position'] == 'Goalkeeper']
    club_stats_2024_field_players = club_stats_2024[club_stats_2024['position'] != 'Goalkeeper']

    predicted_tournament_stats_goalkeepers = predict_rf_for_euro_2024(goalkeeper_models, club_stats_2024_goalkeepers)
    predicted_tournament_stats_field_players = predict_rf_for_euro_2024(field_player_models,
                                                                        club_stats_2024_field_players)

    predicted_tournament_stats = pd.concat(
        [predicted_tournament_stats_goalkeepers, predicted_tournament_stats_field_players], ignore_index=True)

    conn = sqlite3.connect(euro_2024_db_path)
    table_name = 'tournament_stats_predicted_rf_combined'
    predicted_tournament_stats.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Predictions for Euro 2024 saved to table {table_name}")


# Train Random Forest models and use MSE to weigh predictions for the next tournament
def train_rf_with_weighted_mse(tournaments, euro_2024_db_path):
    # Dictionary to store MSE and models for each tournament
    mse_history = {}
    tournament_models = {}
    weights = {}

    # Loop through tournaments and train models
    for tournament in tournaments:
        print(f"\nProcessing {tournament['name']}...")

        # Connect to tournament database
        conn = sqlite3.connect(tournament['db_path'])
        club_stats = pd.read_sql_query("SELECT * FROM club_stats", conn)
        tournament_stats = pd.read_sql_query("SELECT * FROM tournament_stats", conn)
        conn.close()

        # Split data into goalkeepers and field players
        club_stats_goalkeepers = club_stats[club_stats['position'] == 'Goalkeeper']
        club_stats_field_players = club_stats[club_stats['position'] != 'Goalkeeper']

        tournament_stats_goalkeepers = tournament_stats[tournament_stats['position'] == 'Goalkeeper']
        tournament_stats_field_players = tournament_stats[tournament_stats['position'] != 'Goalkeeper']

        # Prepare training data
        X_goalkeepers, y_goalkeepers = prepare_rf_data(club_stats_goalkeepers, tournament_stats_goalkeepers)
        X_field_players, y_field_players = prepare_rf_data(club_stats_field_players, tournament_stats_field_players)

        # Train models for goalkeepers and field players
        goalkeeper_models = train_random_forest_models(X_goalkeepers, y_goalkeepers, position='Goalkeeper')
        field_player_models = train_random_forest_models(X_field_players, y_field_players, position='Field')

        # Predict for Euro 2024 using current models
        conn = sqlite3.connect(euro_2024_db_path)
        club_stats_2024 = pd.read_sql_query("SELECT * FROM club_stats", conn)
        conn.close()

        club_stats_2024_goalkeepers = club_stats_2024[club_stats_2024['position'] == 'Goalkeeper']
        club_stats_2024_field_players = club_stats_2024[club_stats_2024['position'] != 'Goalkeeper']

        # Predict for Euro 2024
        predicted_goalkeepers = predict_rf_for_euro_2024(goalkeeper_models, club_stats_2024_goalkeepers)
        predicted_field_players = predict_rf_for_euro_2024(field_player_models, club_stats_2024_field_players)

        # Combine predictions
        predicted_tournament_stats = pd.concat([predicted_goalkeepers, predicted_field_players], ignore_index=True)

        # Calculate MSE for current tournament models
        mse_goalkeepers = calculate_mse(predicted_goalkeepers, y_goalkeepers)
        mse_field_players = calculate_mse(predicted_field_players, y_field_players)

        mse_total = (mse_goalkeepers + mse_field_players) / 2
        mse_history[tournament['name']] = mse_total
        print(f"MSE for {tournament['name']}: {mse_total}")

        # Save models and calculate weights (the smaller the MSE, the higher the weight)
        tournament_models[tournament['name']] = {
            'goalkeepers': goalkeeper_models,
            'field_players': field_player_models
        }
        weights[tournament['name']] = 1 / mse_total if mse_total != 0 else 1  # Avoid division by zero

    # Normalize weights to sum to 1
    total_weight = sum(weights.values())
    for tournament in weights:
        weights[tournament] /= total_weight
        print(f"Weight for {tournament}: {weights[tournament]}")

    # Predict Euro 2024 using weighted average of models
    final_predictions_goalkeepers = weighted_average_predictions(tournament_models, club_stats_2024_goalkeepers, weights, 'goalkeepers')
    final_predictions_field_players = weighted_average_predictions(tournament_models, club_stats_2024_field_players, weights, 'field_players')

    # Combine final predictions
    final_predictions = pd.concat([final_predictions_goalkeepers, final_predictions_field_players], ignore_index=True)

    # Synchronize the number_of_matches for all positions within the same team
    final_predictions = synchronize_number_of_matches(final_predictions)

    # Save final predictions to the database
    conn = sqlite3.connect(euro_2024_db_path)
    table_name = 'final_tournament_stats_predicted_rf_weighted'
    final_predictions.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

    print(f"Final predictions for Euro 2024 saved to table {table_name}")
    return final_predictions, mse_history


# Function to compute a weighted average of predictions
def weighted_average_predictions(tournament_models, club_stats_2024, weights, position_type):
    weighted_predictions = None

    for tournament, models in tournament_models.items():
        print(f"Predicting for Euro 2024 with {tournament} {position_type} models (weight: {weights[tournament]})")

        # Get the appropriate model for the position type (goalkeepers or field players)
        model = models[position_type]
        predictions = predict_rf_for_euro_2024(model, club_stats_2024)

        # Filter only numeric columns
        predictions_numeric = predictions.select_dtypes(include=[np.number])

        # Multiply predictions by the tournament weight
        weighted_predictions_tournament = predictions_numeric * weights[tournament]

        # Sum the weighted predictions
        if weighted_predictions is None:
            weighted_predictions = weighted_predictions_tournament
        else:
            weighted_predictions += weighted_predictions_tournament

    # Combine weighted predictions with the non-numeric columns like 'team_id' and 'position'
    non_numeric_columns = predictions.select_dtypes(exclude=[np.number])
    final_predictions = pd.concat([weighted_predictions, non_numeric_columns.reset_index(drop=True)], axis=1)

    # Round the numeric predictions to integers
    final_predictions[weighted_predictions.columns] = final_predictions[weighted_predictions.columns].round().astype(int)

    return final_predictions


# Helper function to calculate MSE
def calculate_mse(predicted_stats, true_stats):
    # Select only numeric columns
    predicted_stats_numeric = predicted_stats.select_dtypes(include=[np.number])
    true_stats_numeric = true_stats.select_dtypes(include=[np.number])

    # Get common columns between predicted and true stats
    common_columns = predicted_stats_numeric.columns.intersection(true_stats_numeric.columns)

    # Filter both dataframes to include only common columns
    predicted_stats_filtered = predicted_stats_numeric[common_columns]
    true_stats_filtered = true_stats_numeric[common_columns]

    # Ensure the lengths of predicted and true stats are equal
    min_length = min(len(predicted_stats_filtered), len(true_stats_filtered))

    # Adjust both sets to the same size if needed
    predicted_stats_adjusted = predicted_stats_filtered.iloc[:min_length]
    true_stats_adjusted = true_stats_filtered.iloc[:min_length]

    # Calculate MSE
    mse = mean_squared_error(true_stats_adjusted, predicted_stats_adjusted)
    return mse


# Define tournaments
tournaments = [
    {"name": "Euro 2008", "db_path": "euro_2008_stats.db"},
    {"name": "Euro 2012", "db_path": "euro_2012_stats.db"},
    {"name": "Euro 2016", "db_path": "euro_2016_stats.db"},
    {"name": "Euro 2020", "db_path": "euro_2020_stats.db"},
    {"name": "WC 2006", "db_path": "WC_2006_stats.db"},
    {"name": "WC 2010", "db_path": "WC_2010_stats.db"},
    {"name": "WC 2014", "db_path": "WC_2014_stats.db"},
    {"name": "WC 2018", "db_path": "WC_2018_stats.db"},
    {"name": "WC 2022", "db_path": "WC_2022_stats.db"},
]

# Run the process
predictions_db_path = 'euro_2024_predicted_stats.db'
euro_2024_db_path = 'euro_2024_stats.db'
copy_club_stats_to_new_db(euro_2024_db_path, predictions_db_path)
final_predictions, mse_history = train_rf_with_weighted_mse(tournaments, predictions_db_path)
