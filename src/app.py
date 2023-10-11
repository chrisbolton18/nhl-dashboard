from flask import Flask, jsonify, request
import requests
import json
from markupsafe import escape_silent

app = Flask(__name__)

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
def getPlayerStats(playerName=None):
    playerID = getPlayerIDByName(playerName)

    isCurrentSeason = escape_silent(request.args.get('current'))
    if len(isCurrentSeason) == 0 or isCurrentSeason != 'True':
        isCurrentSeason = False
    else:
        isCurrentSeason = True

    if playerID == None:
        return "No player found"

    if isCurrentSeason:
        data = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{playerID}/stats?stats=statsSingleSeason&season=20232024')
    else:
        data = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{playerID}/stats?stats=yearByYear')

    if data.status_code != 200:
        return '[]'
    else:
        data = data.json()


    return jsonify(data['stats'])

@app.route('/players/<string:playerName>/accolades')
def getPlayerAccolades(playerName=None):
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
    file_playerIDs = open('playerIDs.json', 'r')
    playerIDs = json.load(file_playerIDs)

    retval = ''

    try:
        retval = playerIDs[player_name]
    except:
        retval = None

    return retval

if __name__ == '__main__':
    app.run()