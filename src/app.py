from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return '[]'

@app.route('/teams/<string:teamName>/stats')
def getTeamStats(teamName=None):
    team_id = getTeamIDByName(teamName)

    if team_id == "error" or team_id == "can't find team":
        return '[]'

    data = requests.get(f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}/stats")
    if data.status_code != 200:
        return '[]'
    else:
        data = data.json()
    
    stats = data['stats']

    return jsonify(stats)

@app.route('/players/<string:playerName>/stats')
def getPlayerStats():
    return

def getTeamIDByName(team_name):
    data = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
    if data.status_code != 200:
        return "error"
    else:
        data = data.json()

    teams = data['teams']

    for team in teams:
        name = team['name']

        if name == team_name:
            return str(team['id'])
    
    return "can't find team"

def getPlayerIDByName(player_name):
    

if __name__ == '__main__':
    app.run()