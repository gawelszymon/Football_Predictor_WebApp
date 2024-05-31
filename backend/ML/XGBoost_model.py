import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

# Tworzenie przykładowych danych dla Tabeli Reprezentacji
data_reprezentacje = {
    'id': [1, 2, 3],
    'nazwa': ['Reprezentacja A', 'Reprezentacja B', 'Reprezentacja C'],
    'ranking_FIFA': [5, 10, 15],
    'wyniki_2_euro': [0, 1, 2],
    'wyniki_2_ms': [1, 0, 2],
    'srednia_wynikow_zawodnikow': [7.5, 6.8, 7.1],
    'ilosc_obroncow': [4, 5, 4],
    'ilosc_pomocnikow': [3, 2, 4],
    'ilosc_napastnikow': [3, 3, 2],
    'liczba_udzialow_w_Mistrzostwach_Swiata': [10, 8, 5],
    'liczba_udzialow_w_EURO': [8, 10, 7]
}

# Tworzenie przykładowych danych dla Tabeli Meczy
data_mecze = {
    'id_meczu': [1, 2, 3],
    'reprezentacja_a': [1, 1, 2],
    'reprezentacja_b': [2, 3, 3],
    'gole_a': [2, 1, 3],
    'gole_b': [1, 2, 2]
}

# Konwersja do DataFrame
df_reprezentacje = pd.DataFrame(data_reprezentacje)
df_mecze = pd.DataFrame(data_mecze)

# Łączenie danych meczy z danymi reprezentacji
df_mecze = df_mecze.merge(df_reprezentacje, left_on='reprezentacja_a', right_on='id', suffixes=('', '_a'))
df_mecze = df_mecze.merge(df_reprezentacje, left_on='reprezentacja_b', right_on='id', suffixes=('', '_b'))

# Usunięcie niepotrzebnych kolumn typu object
df_mecze = df_mecze.drop(columns=['nazwa', 'nazwa_b'])

# Przygotowanie cech i etykiet
X = df_mecze.drop(columns=['id_meczu', 'id', 'id_b', 'gole_a', 'gole_b'])  # Usuń kolumny, które nie są cechami
y_a = df_mecze['gole_a']  # Etykiety dla liczby bramek strzelonych przez drużynę A
y_b = df_mecze['gole_b']  # Etykiety dla liczby bramek strzelonych przez drużynę B

# Podział danych na zbiór treningowy i testowy dla drużyny A
X_train_a, X_test_a, y_train_a, y_test_a = train_test_split(X, y_a, test_size=0.2, random_state=42)

# Definiowanie modelu XGBoost Regressor dla drużyny A
model_a = XGBRegressor(n_estimators=100, random_state=42)

# Trenowanie modelu dla drużyny A
model_a.fit(X_train_a, y_train_a)

# Przewidywanie na zbiorze testowym dla drużyny A
y_pred_a = model_a.predict(X_test_a)

# Ocena modelu dla drużyny A
# mse_a = mean_squared_error(y_test_a, y_pred_a)
# print(f'Mean Squared Error for Team A: {mse_a}')
# print(f'Predicted values for Team A: {y_pred_a}')
# print(f'True values for Team A: {y_test_a.values}')

# Podział danych na zbiór treningowy i testowy dla drużyny B
X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X, y_b, test_size=0.2, random_state=42)

# Definiowanie modelu XGBoost Regressor dla drużyny B
model_b = XGBRegressor(n_estimators=100, random_state=42)

# Trenowanie modelu dla drużyny B
model_b.fit(X_train_b, y_train_b)

# Przewidywanie na zbiorze testowym dla drużyny B
y_pred_b = model_b.predict(X_test_b)

# Ocena modelu dla drużyny B
# mse_b = mean_squared_error(y_test_b, y_pred_b)
# print(f'Mean Squared Error for Team B: {mse_b}')
# print(f'Predicted values for Team B: {y_pred_b}')
# print(f'True values for Team B: {y_test_b.values}')

# Zaokrąglanie wartości predykcji
y_pred_a_rounded = round(y_pred_a[0])
y_pred_b_rounded = round(y_pred_b[0])

print(f'Predicted: [Team A] {y_pred_a_rounded}: {y_pred_b_rounded} [Team B]')
print(f'True: [Team A] {y_test_a.values[0]} : {y_test_b.values[0]} [Team B]')
