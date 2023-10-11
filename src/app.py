from flask import Flask, jsonify, request
import requests
import json
from markupsafe import escape_silent
import datetime

app = Flask(__name__)

CURRENT_SEASON = '20232024'
SEASON_START = '2023-10-10'

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

@app.route('/players/<string:playerName>/gameByGame')
def getPlayerGameByGame(playerName=None):
    team_ids = getPlayerTeams(playerName)
    player_id = getPlayerIDByName(playerName)

    last = escape_silent(request.args.get('last'))

    playerSeasonStats = []

    today = datetime.date.today().strftime("%Y-%m-%d")

    for team_id in team_ids:
        data = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?teamId={team_id}&startDate={SEASON_START}&endDate={today}')
        if data.status_code != 200:
            continue
        else:
            data = data.json()

        games = data['dates']

        for game in games:
            game_data = game['games'][0]

            game_id = game_data['gamePk']

            # get boxscore game

            data = requests.get(f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore')
            if data.status_code != 200:
                continue
            else:
                data = data.json()

            game_players = {}
            if data['teams']['away']['team']['id'] == team_id:
                game_players = data['teams']['away']['players']
            else:
                game_players = data['teams']['home']['players']

            try:
                player_game_data = game_players['ID' + str(player_id)]
                playerSeasonStats.append(player_game_data['stats'])
            except:
                continue

    n = len(playerSeasonStats)

    try:
        last = int(last)
    except:
        last = n
        
    playerSeasonStats = playerSeasonStats[(n - last)::]
    return jsonify(playerSeasonStats)

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

def getPlayerTeams(playerName, season=None):

    if season == None:
        season = CURRENT_SEASON

    team_ids = []

    playerID = getPlayerIDByName(playerName)

    data = requests.get(f'https://statsapi.web.nhl.com/api/v1/people/{playerID}/stats?stats=yearByYear')
    if data.status_code != 200:
        return '[]'
    else:
        data = data.json()

    yearByYear = data['stats'][0]['splits']

    for year in yearByYear:
        thisSeason = year['season']

        if thisSeason == season:
            team_ids.append(year['team']['id'])

    return team_ids
    

if __name__ == '__main__':
    app.run()