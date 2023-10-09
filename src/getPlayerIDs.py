import requests
import json

retval = {}

teamdata = requests.get('https://statsapi.web.nhl.com/api/v1/teams/')
teamdata = teamdata.json()
teams = teamdata['teams']

for team in teams:
    team_id = team['id']
    teamdata = requests.get(f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/roster')
    teamdata = teamdata.json()

    roster = teamdata['roster']

    for player in roster:
        player_data = player['person']
        retval[player_data['fullName']] = player_data['id']


with open('playerIDs.json', 'w') as json_file:
    json.dump(retval, json_file)