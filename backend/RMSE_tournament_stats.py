import matplotlib.pyplot as plt
import pandas as pd
import os
from sklearn.metrics import mean_squared_error
import numpy as np

# Tworzenie folderu na wykresy
output_folder = 'rmse_comparison_plots'
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

# Funkcja do zbierania RMSE dla danej statystyki w zależności od pozycji
def gather_rmse_by_position(errors_data, positions, column):
    rmse_by_position = {}
    for position in positions:
        position_data = errors_data[errors_data['position'] == position]
        actual = position_data[f'{column}_actual'].dropna()
        predicted = position_data[f'{column}_predicted'].dropna()

        if len(actual) > 0 and len(predicted) > 0:
            rmse_value = calculate_rmse(actual, predicted)
            rmse_by_position[position] = rmse_value
        else:
            rmse_by_position[position] = None

    return rmse_by_position

# Funkcja do rysowania wykresu RMSE dla jednej statystyki
def plot_rmse_for_stat(rmse_by_position, stat, output_folder):
    positions = [pos for pos in rmse_by_position if rmse_by_position[pos] is not None]
    rmse_values = [rmse_by_position[pos] for pos in positions]

    if len(positions) == 0:
        print(f"Brak dostępnych danych dla statystyki {stat}.")
        return

    # Rysowanie wykresu
    plt.figure(figsize=(10, 6))
    plt.bar(positions, rmse_values, color=['blue', 'green', 'red', 'orange'][:len(positions)])
    plt.title(f'Porównanie RMSE dla statystyki: {stat}')
    plt.xlabel('Pozycja')
    plt.ylabel('RMSE')
    plt.tight_layout()

    # Zapis do pliku
    filepath = os.path.join(output_folder, f'rmse_comparison_{stat}.png')
    plt.savefig(filepath)
    print(f"Wykres RMSE dla statystyki {stat} zapisany: {filepath}")
    plt.close()

# Wczytaj dane
errors_data = pd.read_csv('errors_comparison.csv')

# Definiowanie pozycji i statystyk
positions = ['Goalkeeper', 'Defense', 'Midfield', 'Attack']
stats = ['minutes', 'yellow_cards', 'red_cards', 'goals', 'assists', 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence']

# Przeglądanie każdej statystyki, zbieranie RMSE dla każdej pozycji i rysowanie wykresu
for stat in stats:
    # Pomiń gole i asysty dla bramkarzy
    if stat in ['goals', 'assists']:
        rmse_by_position = gather_rmse_by_position(errors_data[errors_data['position'] != 'Goalkeeper'], positions, stat)
    else:
        rmse_by_position = gather_rmse_by_position(errors_data, positions, stat)

    plot_rmse_for_stat(rmse_by_position, stat, output_folder)
