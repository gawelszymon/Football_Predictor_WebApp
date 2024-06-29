from flask import Flask, jsonify, render_template
from flask_cors import CORS
from euro_groups import get_teams_info

app = Flask(__name__, template_folder="../frontend/templates", static_folder='../frontend/static')
CORS(app)


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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
