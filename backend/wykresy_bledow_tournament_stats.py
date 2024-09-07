import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Tworzenie folderu na wykresy
output_folder = 'prediction_plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Funkcja do normalizacji błędu
def normalize_error(actual, predicted):
    try:
        error = actual - predicted
        range_val = actual.max() - actual.min()
        if range_val == 0:  # Jeśli brak zmienności
            print("Brak zmienności w danych, brak normalizacji.")
            return error  # Zwracamy błąd bez normalizacji
        return error / range_val
    except Exception as e:
        print(f"Błąd normalizacji: {e}")
        return actual - predicted  # Zwracamy błąd bez normalizacji

# Funkcja do rysowania błędów jednej kolumny
def plot_single_error(position, data, column, color, output_folder):
    error = normalize_error(data[f'{column}_actual'], data[f'{column}_predicted'])

    # Tworzenie wykresu dla pojedynczej kolumny
    plt.figure(figsize=(7, 6))
    plt.hist(error.dropna(), bins=30, color=color, label=f'Błąd: {column}')
    plt.title(f'Błąd predykcji {column} dla pozycji: {position}')
    plt.xlabel('Znormalizowany błąd' if (data[f'{column}_actual'].max() - data[f'{column}_actual'].min()) != 0 else 'Błąd')
    plt.ylabel('Liczba przypadków')
    plt.legend()
    plt.tight_layout()

    # Zapis do pliku
    filename = f"{position}_{column}_error.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath)
    print(f"Wykres zapisany: {filepath}")
    plt.close()

# Funkcja do rysowania dwóch błędów na jednym obrazku
def plot_two_errors(position, data, column1, column2, color1, color2, output_folder):
    error1 = normalize_error(data[f'{column1}_actual'], data[f'{column1}_predicted'])
    error2 = normalize_error(data[f'{column2}_actual'], data[f'{column2}_predicted'])

    # Tworzenie wykresu z dwoma subplots
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Błędy predykcji dla pozycji: {position}', fontsize=16)

    # Wykres dla pierwszej kolumny
    axs[0].hist(error1.dropna(), bins=30, color=color1, label=f'Błąd: {column1}')
    axs[0].set_title(f'Błąd predykcji {column1}')
    axs[0].set_xlabel('Znormalizowany błąd' if (data[f'{column1}_actual'].max() - data[f'{column1}_actual'].min()) != 0 else 'Błąd')
    axs[0].set_ylabel('Liczba przypadków')
    axs[0].legend()

    # Wykres dla drugiej kolumny
    axs[1].hist(error2.dropna(), bins=30, color=color2, label=f'Błąd: {column2}')
    axs[1].set_title(f'Błąd predykcji {column2}')
    axs[1].set_xlabel('Znormalizowany błąd' if (data[f'{column2}_actual'].max() - data[f'{column2}_actual'].min()) != 0 else 'Błąd')
    axs[1].set_ylabel('Liczba przypadków')
    axs[1].legend()

    # Zapis do pliku
    filename = f"{position}_{column1}_and_{column2}_error.png"
    filepath = os.path.join(output_folder, filename)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(filepath)
    print(f"Wykres zapisany: {filepath}")
    plt.close()

# Wczytaj dane
errors_data = pd.read_csv('errors_comparison.csv')

# Definiowanie pozycji i kolorów dla każdej statystyki
positions = ['Goalkeeper', 'Defense', 'Midfield', 'Attack']
columns_by_position = {
    'Goalkeeper': ['minutes', 'yellow_cards', 'red_cards', 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches'],
    'Defense': ['minutes', 'yellow_cards', 'red_cards', 'goals', 'assists', 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches'],
    'Midfield': ['minutes', 'yellow_cards', 'red_cards', 'goals', 'assists', 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches'],
    'Attack': ['minutes', 'yellow_cards', 'red_cards', 'goals', 'assists', 'starting_eleven', 'substituted_in', 'on_bench', 'suspended', 'injured', 'absence', 'number_of_matches']
}
colors = ['blue', 'green', 'red', 'orange', 'purple', 'cyan', 'magenta', 'brown', 'pink', 'gray', 'olive', 'yellow']

# Przeglądanie danych dla każdej pozycji i rysowanie wykresów
for position in positions:
    print(f'\nAnaliza dla pozycji: {position}')
    position_data = errors_data[errors_data['position'] == position]
    columns = columns_by_position[position]

    # Iteracja parami kolumn
    for i in range(0, len(columns), 2):
        column1 = columns[i]
        column2 = columns[i+1] if i+1 < len(columns) else None

        if column2 is not None:
            # Sprawdzenie, czy kolumny mają dostępne dane
            if position_data[f'{column1}_actual'].notnull().any() and position_data[f'{column1}_predicted'].notnull().any() and \
               position_data[f'{column2}_actual'].notnull().any() and position_data[f'{column2}_predicted'].notnull().any():
                plot_two_errors(position, position_data, column1, column2, colors[i], colors[i+1], output_folder)
            else:
                print(f'Brak danych dla {column1} lub {column2} na pozycji {position}.')
        else:
            # Rysowanie wykresu dla pojedynczej kolumny
            if position_data[f'{column1}_actual'].notnull().any() and position_data[f'{column1}_predicted'].notnull().any():
                plot_single_error(position, position_data, column1, colors[i], output_folder)
            else:
                print(f'Brak danych dla {column1} na pozycji {position}.')
