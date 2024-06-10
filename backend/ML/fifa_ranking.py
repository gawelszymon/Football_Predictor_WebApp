import requests
import json

# URL API
url = "https://inside.fifa.com/api/ranking-overview?locale=en&dateId=id14338"

# Nagłówki HTTP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://inside.fifa.com/fifa-world-ranking/men?dateId=id14338"
}

# Pobierz dane z API
response = requests.get(url, headers=headers)

# Sprawdź status odpowiedzi
if response.status_code == 200:
    try:
        data = response.json()
        # Pobierz tylko totalPoints oraz alt
        selected_data = []
        for item in data['rankings']:
            id_team = item['rankingItem']['idTeam']
            name = item['rankingItem']['name']
            total_points = item['rankingItem']['totalPoints']
            selected_data.append({
                'id': id_team,
                'name': name,
                'totalPoints': total_points,
            })

        # Zapisz wybrane dane do pliku JSON
        with open('selected_ranking_items.json', 'w') as json_file:
            json.dump(selected_data, json_file, indent=4)
        print("Dane zostały zapisane do pliku selected_ranking_items.json")
    except requests.exceptions.JSONDecodeError:
        print("Błąd dekodowania JSON: Odpowiedź nie jest poprawnym JSON.")
else:
    print(f"Błąd: Otrzymano status odpowiedzi {response.status_code}")

# Wypisz treść odpowiedzi dla debugowania
print(response.text)
