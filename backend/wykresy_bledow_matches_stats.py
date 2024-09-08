import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Mapa team_id do nazw krajów
team_id_to_country = {
    3262: 'Germany', 3299: 'England', 3300: 'Portugal', 3375: 'Spain', 3376: 'Italy',
    3377: 'France', 3379: 'Netherlands', 3380: 'Scotland', 3381: 'Turkey', 3382: 'Belgium',
    3383: 'Austria', 3384: 'Switzerland', 3436: 'Denmark', 3438: 'Serbia', 3442: 'Poland',
    3445: 'Czech Republic', 3447: 'Romania', 3468: 'Hungary', 3503: 'Slovakia', 3556: 'Croatia',
    3561: 'Albania', 3588: 'Slovenia', 3699: 'Ukraine', 3669: 'Georgia'
}

# Tworzenie folderu na wykresy
output_folder = 'repka_goals_plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Funkcja do normalizacji błędu
def normalize_error(error):
    try:
        range_val = error.max() - error.min()
        if range_val == 0:  # Jeśli brak zmienności
            print("Brak zmienności w danych, brak normalizacji.")
            return error  # Zwracamy błąd bez normalizacji
        return error / range_val
    except Exception as e:
        print(f"Błąd normalizacji: {e}")
        return error  # Zwracamy błąd bez normalizacji

# Funkcja do rysowania błędów goli dla reprezentacji
def plot_team_errors(data, team_id, column1, column2, color1, color2, output_folder, team_name):
    error1 = normalize_error(data[column1])
    error2 = normalize_error(data[column2])

    # Tworzenie wykresu z dwoma subplots
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Błędy predykcji dla {team_name}', fontsize=16)

    # Wykres dla błędu reprezentacji
    axs[0].hist(error1.dropna(), bins=30, color=color1, label=f'Błąd: {team_name}')
    axs[0].set_title(f'Błąd goli {team_name}')
    axs[0].set_xlabel('Znormalizowany błąd' if (error1.max() - error1.min()) != 0 else 'Błąd')
    axs[0].set_ylabel('Liczba przypadków')
    axs[0].legend()

    # Wykres dla błędu przeciwników
    axs[1].hist(error2.dropna(), bins=30, color=color2, label=f'Błąd: Opponents')
    axs[1].set_title('Błąd goli Opponents')
    axs[1].set_xlabel('Znormalizowany błąd' if (error2.max() - error2.min()) != 0 else 'Błąd')
    axs[1].set_ylabel('Liczba przypadków')
    axs[1].legend()

    # Zapis do pliku
    filename = f"{team_name}_vs_opponents_goals_error.png"
    filepath = os.path.join(output_folder, filename)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(filepath)
    print(f"Wykres zapisany: {filepath}")
    plt.close()

# Funkcja do porównania rzeczywistych wyników z przewidywaniami
def calculate_match_outcome_errors(data, team_id, team_name):
    actual_wins, actual_draws, actual_losses = 0, 0, 0
    predicted_wins, predicted_draws, predicted_losses = 0, 0, 0

    for idx, row in data.iterrows():
        team1_goals_actual = row['team1_goals']
        team2_goals_actual = row['team2_goals']
        team1_goals_predicted = row['team1_goals_predicted']
        team2_goals_predicted = row['team2_goals_predicted']

        # Wyniki rzeczywiste
        if team_id == row['team1_id']:
            if team1_goals_actual > team2_goals_actual:
                actual_wins += 1
            elif team1_goals_actual == team2_goals_actual:
                actual_draws += 1
            else:
                actual_losses += 1
        elif team_id == row['team2_id']:
            if team2_goals_actual > team1_goals_actual:
                actual_wins += 1
            elif team2_goals_actual == team1_goals_actual:
                actual_draws += 1
            else:
                actual_losses += 1

        # Wyniki przewidywane
        if team_id == row['team1_id']:
            if team1_goals_predicted > team2_goals_predicted:
                predicted_wins += 1
            elif team1_goals_predicted == team2_goals_predicted:
                predicted_draws += 1
            else:
                predicted_losses += 1
        elif team_id == row['team2_id']:
            if team2_goals_predicted > team1_goals_predicted:
                predicted_wins += 1
            elif team2_goals_predicted == team1_goals_predicted:
                predicted_draws += 1
            else:
                predicted_losses += 1

    # Wyświetlenie statystyk dla reprezentacji
    print(f"\nStatystyki dla {team_name}:")
    print(f"Rzeczywiste wygrane: {actual_wins}, remisy: {actual_draws}, przegrane: {actual_losses}")
    print(f"Przewidywane wygrane: {predicted_wins}, remisy: {predicted_draws}, przegrane: {predicted_losses}")

# Wczytaj dane
penalties_errors_file = 'errors_comparison_penalties.csv'
errors_data = pd.read_csv(penalties_errors_file)

# Definiowanie kolumn do analizy (dla goli i przewidywań)
columns = ['team1_goals_error', 'team2_goals_error']
colors = ['blue', 'green']

# Tworzenie wykresów i analiz dla każdej reprezentacji
for team_id, team_name in team_id_to_country.items():
    team_data = errors_data[(errors_data['team1_id'] == team_id) | (errors_data['team2_id'] == team_id)]

    # Rysowanie wykresów dla błędów w przewidywaniach goli
    if not team_data.empty:
        plot_team_errors(team_data, team_id, 'team1_goals_error', 'team2_goals_error', 'blue', 'green', output_folder,
                         team_name)

    # Wyświetlanie statystyk błędów przewidywań wyników meczów
    calculate_match_outcome_errors(team_data, team_id, team_name)
