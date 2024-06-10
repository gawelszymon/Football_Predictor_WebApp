import requests
import json

def convert_value(value):
    value = value.replace(',', '.')
    if 'tys' in value:
        value = value.replace('tys. €', '').strip()
        value = float(value) * 1000
    elif 'mln' in value:
        value = value.replace('mln €', '').strip()
        value = float(value) * 1000000
    else:
        value = float(value.replace('€', '').strip())
    return value

id = 38253
# URL API (upewnij się, że jest poprawny)
url = f"https://www.transfermarkt.pl/ceapi/marketValueDevelopment/graph/{id}"

# Nagłówki HTTP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.transfermarkt.pl/robert-lewandowski/marktwertverlauf/spieler/38253"
}

# Pobierz dane z API
response = requests.get(url, headers=headers)

# Sprawdź status odpowiedzi
if response.status_code == 200:
    try:
        data = response.json()
        # Pobierz tylko totalPoints oraz alt
        selected_data = []
        for item in data['list']:
            market_value = item['mw']
            date_mv = item['datum_mw']
            club = item['verein']
            market_value_converted = convert_value(market_value)
            selected_data.append({
                'value': market_value_converted,
                'date': date_mv,
                'club': club,
            })

        # Zapisz wybrane dane do pliku JSON
        with open('transfermarkt_values.json', 'w', encoding='utf-8') as json_file:
            json.dump(selected_data, json_file, ensure_ascii=False, indent=4)
        print("Dane zostały zapisane do pliku transfermarkt_values.json")
    except json.JSONDecodeError:
        print("Błąd dekodowania JSON: Odpowiedź nie jest poprawnym JSON.")
        print("Treść odpowiedzi:")
        print(response.text)
    except ValueError as ve:
        print(f"Błąd konwersji wartości: {ve}")
else:
    print(f"Błąd: Otrzymano status odpowiedzi {response.status_code}")
    print("Treść odpowiedzi:")
    print(response.text)
