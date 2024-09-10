import os
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from euro_groups import get_teams_info
from frontend_last_matches import get_team_matches
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, template_folder="../frontend/templates", static_folder='../frontend/static')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///entries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)
    
with app.app_context():
    db.create_all()
    
RMSE_DIR = 'rmse_comparison_plots'
ATTACK_DIR = 'attack_plots'
MIEDFIELD_DIR = 'miedfield_plots'
DEFENSE_DIR = 'defense_plots'
GOALKEEPER_DIR = 'goalkeeper_plots'
REPKA_GOALS_DIR = 'repka_goals_plots'
REPKA_PRDICTION_DIR = 'repka_prediction_plots'


# entries = [     #TODO replace with database
#     {
#         'username': 'Mesut Oezil',
#         'content': 'CR7 or Leo Messi',
#         'timestamp': '2024-08-28 23:15:00'
#     },
#     {
#         'username': 'Pepe Guardiola',
#         'content': 'LM10, the only goat',
#         'timestamp': '2024-08-28 23:20:00'
#     }
# ]

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

@app.route('/rmse_plots')
def rmse_plots():
    return render_template('rmse_plots.html')

@app.route('/atack_plots')
def atack_plots():
    return render_template('atack_plots.html')

@app.route('/miedfield_plots')
def miedfield_plots():
    return render_template('miedfield_plots.html')

@app.route('/defense_plots')
def defense_plots():
    return render_template('defense_plots.html')

@app.route('/goalkeeper_plots')
def goalkeeper_plots():
    return render_template('goalkeeper_plots.html')

@app.route('/repka_goals_plots')
def repka_goals_plots():
    return render_template('repka_goals_plots.html')

@app.route('/repka_prediction_plots')
def repka_prediction_plots():
    return render_template('repka_prediction_plots.html')

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

@app.route('/forum')
def forum():
    return render_template('forum.html')

@app.route('/add_entry', methods=['POST'])
def add_entry():
    try:
        data = request.json
        if not data or 'username' not in data or 'content' not in data:
            return jsonify({"error": "Missing username or content"}), 400
        
        new_entry = Entry(
            username = data['username'],
            content=data['content'],
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({"message": "Entry added successfully!"})
        
    except Exception as e:  #to print server logs
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/get_entries', methods=['GET'])
def get_entries():
    entries = Entry.query.all()
    entries_list = [{
        "username": entry.username,
        "content": entry.content,
        "timestamp": entry.timestamp
    } for entry in entries]
    
    return jsonify(entries_list)

@app.route('/rmse_comparison_plots')
def list_images_rmse():
    files = [f for f in os.listdir(RMSE_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/rmse_comparison_plots/<rmse>')
def serve_image(rmse):
    return send_from_directory(RMSE_DIR, rmse)

@app.route('/attack_comparison_plots')
def list_images_attack():
    files = [f for f in os.listdir(ATTACK_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/attack_comparison_plots/<attack>')
def serve_image1(attack):
    return send_from_directory(ATTACK_DIR, attack)

@app.route('/miedfield_comparison_plots')
def list_images_miedfield():
    files = [f for f in os.listdir(MIEDFIELD_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/miedfield_comparison_plots/<miedfield>')
def serve_image2(miedfield):
    return send_from_directory(MIEDFIELD_DIR, miedfield)

@app.route('/defense_comparison_plots')
def list_images_defense():
    files = [f for f in os.listdir(DEFENSE_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/defense_comparison_plots/<defense>')
def serve_image3(defense):
    return send_from_directory(DEFENSE_DIR, defense)

@app.route('/goalkeeper_comparison_plots')
def list_images_goalkeeper():
    files = [f for f in os.listdir(GOALKEEPER_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/goalkeeper_comparison_plots/<goalkeeper>')
def serve_image4(goalkeeper):
    return send_from_directory(GOALKEEPER_DIR, goalkeeper)

@app.route('/repka_goals_comparison_plots')
def list_images__repka_goals():
    files = [f for f in os.listdir(REPKA_GOALS_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/repka_goals_comparison_plots/<repka_goals>')
def serve_image5(repka_goals):
    return send_from_directory(REPKA_GOALS_DIR, repka_goals)

@app.route('/repka_prediction_comparison_plots')
def list_images__repka_prediction():
    files = [f for f in os.listdir(REPKA_PRDICTION_DIR) if f.endswith('.png')]
    return jsonify(files)

@app.route('/repka_prediction_comparison_plots/<repka_prediction>')
def serve_image6(repka_prediction):
    return send_from_directory(REPKA_PRDICTION_DIR, repka_prediction)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
