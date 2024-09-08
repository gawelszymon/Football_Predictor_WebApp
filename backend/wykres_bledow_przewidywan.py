import matplotlib.pyplot as plt
import pandas as pd
import os

# Mapa team_id do nazw krajów
team_id_to_country = {
    3262: 'Germany', 3299: 'England', 3300: 'Portugal', 3375: 'Spain', 3376: 'Italy',
    3377: 'France', 3379: 'Netherlands', 3380: 'Scotland', 3381: 'Turkey', 3382: 'Belgium',
    3383: 'Austria', 3384: 'Switzerland', 3436: 'Denmark', 3438: 'Serbia', 3442: 'Poland',
    3445: 'Czech Republic', 3447: 'Romania', 3468: 'Hungary', 3503: 'Slovakia', 3556: 'Croatia',
    3561: 'Albania', 3588: 'Slovenia', 3699: 'Ukraine', 3669: 'Georgia'
}

# Tworzenie folderu na wykresy
output_folder = 'repka_prediction_plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Funkcja do porównania rzeczywistych wyników z przewidywaniami i stworzenia danych do wykresu
def calculate_match_outcome_errors(data, team_id, team_name):
    actual_wins, actual_draws, actual_losses = 0, 0, 0
    predicted_wins, predicted_draws, predicted_losses = 0, 0, 0
    correct_outcome = 0
    exact_score = 0
    incorrect_outcome = 0

    for idx, row in data.iterrows():
        team1_goals_actual = row['team1_goals']
        team2_goals_actual = row['team2_goals']
        team1_goals_predicted = row['team1_goals_predicted']
        team2_goals_predicted = row['team2_goals_predicted']

        # Wyniki rzeczywiste
        if team_id == row['team1_id']:
            actual_result = 'win' if team1_goals_actual > team2_goals_actual else 'draw' if team1_goals_actual == team2_goals_actual else 'loss'
            predicted_result = 'win' if team1_goals_predicted > team2_goals_predicted else 'draw' if team1_goals_predicted == team2_goals_predicted else 'loss'
        else:
            actual_result = 'win' if team2_goals_actual > team1_goals_actual else 'draw' if team2_goals_actual == team1_goals_actual else 'loss'
            predicted_result = 'win' if team2_goals_predicted > team1_goals_predicted else 'draw' if team2_goals_predicted == team1_goals_predicted else 'loss'

        # Zliczanie rzeczywistych wyników
        if actual_result == 'win':
            actual_wins += 1
        elif actual_result == 'draw':
            actual_draws += 1
        else:
            actual_losses += 1

        # Zliczanie przewidywanych wyników
        if predicted_result == 'win':
            predicted_wins += 1
        elif predicted_result == 'draw':
            predicted_draws += 1
        else:
            predicted_losses += 1

        # Sprawdzanie poprawności przewidywań
        if actual_result == predicted_result:
            correct_outcome += 1
            # Sprawdzanie, czy wynik był dokładnie taki sam (dokładne liczby goli)
            if team1_goals_actual == team1_goals_predicted and team2_goals_actual == team2_goals_predicted:
                exact_score += 1
        else:
            incorrect_outcome += 1

    # Statystyki
    print(f"\nStatystyki dla {team_name}:")
    print(f"Rzeczywiste wygrane: {actual_wins}, remisy: {actual_draws}, przegrane: {actual_losses}")
    print(f"Przewidywane wygrane: {predicted_wins}, remisy: {predicted_draws}, przegrane: {predicted_losses}")
    print(f"Poprawnie przewidziane wyniki: {correct_outcome}, z tego dokładne wyniki: {exact_score}, błędne wyniki: {incorrect_outcome}")

    return correct_outcome, incorrect_outcome, exact_score

# Funkcja do tworzenia wykresu słupkowego
def plot_bar_chart(correct_outcome, exact_score, incorrect_outcome, output_folder, team_name):
    labels = ['Poprawne wyniki', 'Dokładne wyniki', 'Niepoprawne wyniki']
    values = [correct_outcome, exact_score, incorrect_outcome]
    colors = ['lightgreen', 'deepskyblue', 'lightcoral']

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=colors)
    plt.title(f"Szczegóły przewidywań wyników dla {team_name}")
    plt.ylabel("Liczba przypadków")

    filename = f"{team_name}_prediction_details_bar.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath)
    print(f"Wykres słupkowy zapisany: {filepath}")
    plt.close()

# Wczytaj dane
penalties_errors_file = 'errors_comparison_penalties.csv'
errors_data = pd.read_csv(penalties_errors_file)

# Tworzenie wykresów i analiz dla każdej reprezentacji
for team_id, team_name in team_id_to_country.items():
    team_data = errors_data[(errors_data['team1_id'] == team_id) | (errors_data['team2_id'] == team_id)]

    if not team_data.empty:
        # Oblicz poprawność przewidywań
        correct_outcome, incorrect_outcome, exact_score = calculate_match_outcome_errors(team_data, team_id, team_name)

        # Tworzenie wykresu słupkowego dla szczegółów przewidywań
        plot_bar_chart(correct_outcome, exact_score, incorrect_outcome, output_folder, team_name)
