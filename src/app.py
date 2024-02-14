from flask import Flask
import requests
import json
import base64

app = Flask(__name__)

BASE_ENDPOINT = 'https://api-web.nhle.com/v1'
PLAYER_ID_FILENAME = 'data/playerIDs.json'


@app.route('/frontpage/player/stats/<string:player_name>')
def frontpage_player_stats(player_name=None):
    if player_name == None:
        # TODO: handle this
        return 'error: unknown player name'

    player_id = get_id_by_name(player_name)

    if len(player_id) == 0:
        # TODO: handle this
        return "error: can't find player id"

    content = requests.get(
        f'{BASE_ENDPOINT}/player/{player_id}/landing').json()

    # filter relevant data
    retval = filter_frontpage_player_stats(content)

    return retval


@app.route('/frontpage/player/headshot/<string:player_name>')
def frontpage_player_headshot(player_name=None):
    if player_name == None:
        # TODO: handle this
        return 'error: unknown player name'

    player_id = get_id_by_name(player_name)

    if len(player_id) == 0:
        # TODO: handle this
        return "error: can't find player id"

    headshot_endpoint = requests.get(
        f'{BASE_ENDPOINT}/player/{player_id}/landing').json()['headshot']

    response = requests.get(headshot_endpoint, stream=True)

    b64img = base64.b64encode(response.content)
    return b64img


@app.route('/frontpage/player/lastfive/<string:player_name>')
def frontpage_player_lastfive(player_name=None):
    if player_name == None:
        # TODO: handle this
        return 'error: unknown player name'

    player_id = get_id_by_name(player_name)

    if len(player_id) == 0:
        # TODO: handle this
        return "error: can't find player id"

    content = requests.get(
        f'{BASE_ENDPOINT}/player/{player_id}/landing').json()

    retval = filter_frontpage_player_lastfive(content)

    return retval


def get_id_by_name(player_name: str):
    f = open(PLAYER_ID_FILENAME)
    data = json.load(f)

    if player_name not in data:
        return ''

    return str(data[player_name])


def filter_frontpage_player_stats(content: dict):
    content = content['featuredStats']
    is_goalie = 'shutouts' in content['regularSeason']['career']

    if is_goalie:
        reg_season_items = ['savePctg', 'goalsAgainstAvg',
                            'gamesPlayed', 'shutouts', 'wins']
    else:
        reg_season_items = ['assists', 'goals', 'plusMinus', 'points', 'pim']

    retval = dict.fromkeys(['career', 'subSeason'])
    retval['career'] = dict()
    retval['subSeason'] = dict()

    for item in reg_season_items:
        career_data = content['regularSeason']['career'][item]
        retval['career'][item] = career_data

        season_data = content['regularSeason']['subSeason'][item]
        retval['subSeason'][item] = season_data

    return retval


# TODO: this is slow. Make it not slow
def filter_frontpage_player_lastfive(content: dict):
    content = content['last5Games']
    is_goalie = 'goalsAgainst' in content[0]
    if is_goalie:
        items = ['decision', 'goalsAgainst', 'savePctg',
                 'shotsAgainst', 'opponentAbbrev']
    else:
        items = ['gameDate', 'goals', 'assists', 'pim', 'opponentAbbrev']

    retval = [dict() for _ in range(5)]
    for i, game in enumerate(content):
        for item in items:
            retval[i][item] = game[item]

        retval[i]['score'], retval[i]['win'] = get_game_result(
            game['gameId'], home_road_flag=game['homeRoadFlag'])

        retval[i]['opponentLogo'] = get_opponent_logo(
            game['gameId'], home_road_flag=game['homeRoadFlag'])

        retval[i]['homeRoadFlag'] = game['homeRoadFlag']

    return retval


# returns game score formatted as {home team}-{away team}_{home score}-{away score}
# example: detroit beats toronto 3-2 ---> DET-TOR_3-2
def get_game_result(game_id: int, home_road_flag: str = None):
    response = requests.get(
        f'{BASE_ENDPOINT}/gamecenter/{game_id}/boxscore')

    if response.status_code != 200:
        return 'error: '

    content = response.json()

    home_team = content['homeTeam']['abbrev']
    away_team = content['awayTeam']['abbrev']
    home_score = content['homeTeam']['score']
    away_score = content['awayTeam']['score']

    if home_road_flag == 'R':
        return f'{home_team}_{home_score}-{away_score}', (away_score > home_score)
    elif home_road_flag == 'H':
        return f'{away_team}_{home_score}-{away_score}', (home_score > away_score)

    return f'{home_team}-{away_team}_{home_score}-{away_score}', (home_score > away_score)


def get_opponent_logo(game_id: int, home_road_flag: str = 'H'):
    response = requests.get(
        f'{BASE_ENDPOINT}/gamecenter/{game_id}/boxscore')

    if response.status_code != 200:
        return 'error: '

    content = response.json()

    if home_road_flag == 'R':
        return content['homeTeam']['logo']
    else:
        return content['awayTeam']['logo']


if __name__ == '__main__':
    app.run(port=8000, debug=True)
