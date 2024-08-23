from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from euro_groups import get_teams_info
from frontend_last_matches import get_team_matches
import json

app = Flask(__name__, template_folder="../frontend/templates", static_folder='../frontend/static')
CORS(app)

with open('euro_results.json', 'r') as f:
    data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/groups')
def groups():
    return render_template('groups.html')

@app.route('/matches')
def matches():
    return render_template('matches.html')

@app.route('/bracket')
def bracket():
    return render_template('bracket.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/euro_groups', methods=['GET'])
def euro_groups():
    data = get_teams_info()
    return jsonify(data)

@app.route('/last_matches', methods=['GET'])
def last_matches():
    team_id = request.args.get('team_id', default=4703, type=int)  # Default to Poland if no team_id is provided
    data = get_team_matches(team_id)
    return jsonify(data)

@app.route('/euro_details', methods=['GET'])
def euro_details():
    match_team1 = request.args.get('team1', type=str)
    match_team2 = request.args.get('team2', type=str)
    if not (match_team1 and match_team2):
            matches = []
            for round_data in data['rounds']:
                for match in round_data['matches']:
                    match_info = {
                        "num": match['num'],
                        "team1": match['team1']['name'],
                        "team2": match['team2']['name'],
                        "score_ft": match['score']['ft']
                    }
                    matches.append(match_info)
            return jsonify(matches)
    
    for round_data in data['rounds']:
        for match in round_data['matches']:
            if (match['team1']['name'] == match_team1 and match['team2']['name'] == match_team2) or (match['team1']['name'] == match_team2 and match['team2']['name'] == match_team1):
                
                result = {
                    "team1": match['team1']['name'],
                    "team2": match['team2']['name'],
                    "score_ft": match['score']['ft']
                }
                return jsonify(result)
    return jsonify({"error": "Match not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
