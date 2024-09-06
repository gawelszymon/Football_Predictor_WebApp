import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from imblearn.over_sampling import SMOTE
import numpy as np


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


# Function to apply SMOTE only for classification targets
def apply_smote(X_train, y_train, column):
    # Sprawdzamy, czy dane mają wartości binarne (np. tylko 0 i 1)
    if len(np.unique(y_train)) == 2 and np.array_equal(np.unique(y_train), [0, 1]):
        print(f"Applying SMOTE to column {column}")
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        return X_resampled, y_resampled
    else:
        # Nie stosujemy SMOTE dla danych ciągłych
        print(f"Skipping SMOTE for column {column}, as it is continuous.")
        return X_train, y_train


# Function to optimize the model for minutes prediction using GridSearchCV
def optimize_rf_model(X_train, y_train):
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }

    rf = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)

    print(f"Best parameters for minutes prediction: {grid_search.best_params_}")
    return grid_search.best_estimator_


# Train Random Forest models with cross-validation
def train_random_forest_models(X, y, position):
    models = {}

    # Define the columns to predict based on position
    if position == 'Goalkeeper':
        columns_to_predict = ['minutes', 'yellow_cards', 'red_cards', 'starting_eleven', 'substituted_in',
                              'on_bench', 'suspended', 'injured', 'absence']
    else:
        columns_to_predict = ['goals', 'assists', 'minutes', 'yellow_cards', 'red_cards', 'starting_eleven',
                              'substituted_in', 'on_bench', 'suspended', 'injured', 'absence']

    for column in columns_to_predict:
        print(f"Training Random Forest model for {column} for position {position}...")

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y[column], test_size=0.2, random_state=42)

        # Apply SMOTE to classification problems
        X_train, y_train = apply_smote(X_train, y_train, column)

        # Special handling for 'minutes' column
        if column == 'minutes':
            print(f"Optimizing model for {column}")
            rf_model = optimize_rf_model(X_train, y_train)
        else:
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

        # Fit model on training data
        rf_model.fit(X_train, y_train)

        # Test the model
        predictions = rf_model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"Test MSE for {column} ({position}): {mse}")
        models[column] = rf_model

    return models


# Predict tournament stats for Euro 2024 using trained models
def predict_rf_for_euro_2024(models, club_stats_2024):
    X_euro_2024 = clean_data(club_stats_2024.drop(columns=['team_id', 'position']))

    predictions = {}
    for column, model in models.items():
        predictions[column] = model.predict(X_euro_2024)

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

# Run workflow
predictions_db_path = 'euro_2024_predicted_stats.db'
euro_2024_db_path = 'euro_2024_stats.db'
copy_club_stats_to_new_db(euro_2024_db_path, predictions_db_path)
run_rf_on_combined_tournaments(tournaments, predictions_db_path)
