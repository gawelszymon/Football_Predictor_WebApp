import matplotlib.pyplot as plt
import pandas as pd
import os
from sklearn.metrics import mean_squared_error
import numpy as np

# Tworzenie folderu na wykresy
output_folder = 'rmse_comparison_plots_for_matches'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Funkcja do obliczania RMSE
def calculate_rmse(actual, predicted):
    try:
        mse = mean_squared_error(actual, predicted)
        return np.sqrt(mse)  # Zwracamy RMSE
    except Exception as e:
        print(f"Błąd obliczania RMSE: {e}")
        return None

# Funkcja do zbierania RMSE dla goli zdobytych i straconych w zależności od drużyny
def gather_rmse_for_goals(errors_data, teams, goals_column, predicted_column, for_scored=True):
    rmse_by_team = {}
    for team_id, team_name in teams.items():
        # Dane, kiedy drużyna jest team1
        team1_data = errors_data[errors_data['team1_id'] == team_id]
        team1_actual = team1_data[goals_column].dropna()
        team1_predicted = team1_data[predicted_column].dropna()

        # Dane, kiedy drużyna jest team2
        team2_data = errors_data[errors_data['team2_id'] == team_id]
        team2_actual = team2_data[goals_column].dropna()
        team2_predicted = team2_data[predicted_column].dropna()

        # Łączenie wyników dla team1 i team2
        actual = pd.concat([team1_actual, team2_actual])
        predicted = pd.concat([team1_predicted, team2_predicted])

        if len(actual) > 0 and len(predicted) > 0:
            rmse_value = calculate_rmse(actual, predicted)
            rmse_by_team[team_name] = rmse_value
        else:
            rmse_by_team[team_name] = None

    return rmse_by_team

# Funkcja do rysowania wykresu RMSE dla jednej statystyki
def plot_rmse_for_stat(rmse_by_team, stat, output_folder, title, suffix):
    teams = [team for team in rmse_by_team if rmse_by_team[team] is not None]
    rmse_values = [rmse_by_team[team] for team in teams]

    if len(teams) == 0:
        print(f"Brak dostępnych danych dla statystyki {stat}.")
        return

    # Rysowanie wykresu
    plt.figure(figsize=(12, 6))
    plt.bar(teams, rmse_values, color=['blue', 'green', 'red', 'orange'][:len(teams)])
    plt.title(f'{title}')
    plt.xlabel('Drużyna')
    plt.ylabel('RMSE')
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Zapis do pliku z unikalną nazwą
    filepath = os.path.join(output_folder, f'rmse_comparison_{stat}_{suffix}.png')
    plt.savefig(filepath)
    print(f"Wykres RMSE dla statystyki {stat} zapisany: {filepath}")
    plt.close()

# Mapa team_id do nazw krajów
team_id_to_country = {
    3262: 'Germany', 3299: 'England', 3300: 'Portugal', 3375: 'Spain', 3376: 'Italy',
    3377: 'France', 3379: 'Netherlands', 3380: 'Scotland', 3381: 'Turkey', 3382: 'Belgium',
    3383: 'Austria', 3384: 'Switzerland', 3436: 'Denmark', 3438: 'Serbia', 3442: 'Poland',
    3445: 'Czech Republic', 3447: 'Romania', 3468: 'Hungary', 3503: 'Slovakia', 3556: 'Croatia',
    3561: 'Albania', 3588: 'Slovenia', 3699: 'Ukraine', 3669: 'Georgia'
}

# Wczytaj dane
errors_data = pd.read_csv('errors_comparison_penalties.csv')

# Sprawdzenie dostępnych kolumn
print(errors_data.columns)

# RMSE dla goli zdobytych (połączone dla team1 i team2)
rmse_by_team_scored = gather_rmse_for_goals(errors_data, team_id_to_country, 'team1_goals', 'team1_goals_predicted')
plot_rmse_for_stat(rmse_by_team_scored, 'team1_goals', output_folder, "RMSE dla goli zdobytych", "scored")

# RMSE dla goli straconych (połączone dla team1 i team2)
rmse_by_team_conceded = gather_rmse_for_goals(errors_data, team_id_to_country, 'team1_goals', 'team2_goals_predicted', for_scored=False)
plot_rmse_for_stat(rmse_by_team_conceded, 'team1_goals', output_folder, "RMSE dla goli straconych (gole przeciwnika)", "conceded")
