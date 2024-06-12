from flask import Flask, jsonify
from flask_cors import CORS
from euro_groups import get_teams_info

app = Flask(__name__)
CORS(app)

@app.route('/euro_groups', methods=['GET'])
def euro_groups():
    data = get_teams_info()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
