# webapi.py
#
# Interface for providing data from Steam servers to Civ 6 Picker web app

from flask import Flask
import requests
from dotenv import load_dotenv
import os
from helpers import *

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
CIV6_APPID = "289070"

LEADERS_FILE = './data/leaders.txt'
ACH_REF_FILE = './data/ach_ref.json'

LEADER_LIST = import_list_from_file(LEADERS_FILE)
ACH_REF_DICT = build_achievement_reference(ACH_REF_FILE, STEAM_API_KEY, CIV6_APPID)

app = Flask(__name__)


@app.route('/getall')
def get_all_leaders():
    """
    Return a dict containing a dict of all leader-specific achievements and a list of all leaders
    :return: Dictionary
        {
            "achievements": Dictionary,
            "leader_list": List
        }
    """
    all_leader_achievements = {
        "leader_list": LEADER_LIST,
        "achievements": ACH_REF_DICT
    }
    return all_leader_achievements


@app.route('/getuserall/<player_id>')
def get_all_leaders_for_user(player_id):
    """
    Get achievement data for specified user, then return a dict containing another dict of leader-specific achievements
    the user has not yet achieved, as well as a list of all leaders with outstanding achievements
    :param player_id: String-formatted int
    :return: Dictionary
        {
            "achievements": Dictionary,
            "leader_list": List
        }
    """
    try:
        int(player_id)
    except ValueError:
        return "Invalid Steam ID", 404

    steam_api_response = get_player_data(player_id)
    if steam_api_response.status_code == 200:
        user_achivement_data = steam_api_response.json()
        if user_achivement_data["playerstats"]["success"] is True:
            user_data_indexed = index_player_achievements(user_achivement_data)
            user_dict = get_filtered_achievements_for_user(user_data_indexed, ACH_REF_DICT)
            return user_dict
    elif steam_api_response.status_code == 403:
        error_response = steam_api_response.json()
        if error_response["playerstats"]["error"]:
            return error_response["playerstats"]["error"], 403
    else:
        return "Invalid Steam ID", 404


def get_player_data(player_id):
    player_data_url = (
        f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
        f"?appid={CIV6_APPID}"
        f"&key={STEAM_API_KEY}"
        f"&steamid={player_id})"
        f"&l=English"
    )

    response = requests.get(player_data_url)

    return response


# Legacy code for server-side random logic
"""
@app.route('/getuserrandom/<player_id>')
def get_user_random_leader(player_id):
    steam_api_response = get_player_data(player_id)
    if steam_api_response.status_code == 200:
        user_achivement_data = steam_api_response.json()
        if user_achivement_data["playerstats"]["success"] is True:
            ach_selection = select_leader_achievements(user_achivement_data)
            ach_selection_icons = append_achievement_icons(ach_selection)
            return ach_selection_icons
    elif steam_api_response.status_code == 403:
        error_response = steam_api_response.json()
        if error_response["playerstats"]["error"]:
            return error_response["playerstats"]["error"], 403
    else:
        return "Invalid Steam ID", 404


@app.route('/getrandom')
def get_random_leader():
    random_leader = random.choice(LEADER_LIST)
    leader_achievements = get_all_achievements_for_leader(random_leader, ACH_REF_DICT)
    leader_achievements_icons = append_achievement_icons(leader_achievements)
    return leader_achievements_icons


def get_game_data():
    game_data_url = (
        f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
        f"?key={STEAM_API_KEY}"
        f"&appid={CIV6_APPID}"
    )

    r = requests.get(game_data_url)
    if r.status_code == 200:
        response_dict = r.json()
        return response_dict
    else:
        # TODO: Add error logic
        return


def select_leader_achievements(user_achievement_data):
    # print("Processing user data...")
    user_data_indexed = index_player_achievements(user_achievement_data)
    random_leader = get_random_leader_from_achievements(user_data_indexed, ACH_REF_DICT)
    outstanding_achievements = get_outstanding_achievements_by_leader(random_leader, user_data_indexed, ACH_REF_DICT)
    print(json.dumps(outstanding_achievements, indent=4))
    return outstanding_achievements


def append_achievement_icons(ach_selection):
    ach_selection_icons = ach_selection
    game_data = get_game_data()
    if game_data:
        for achievement in game_data["game"]["availableGameStats"]["achievements"]:
            if achievement["name"] in ach_selection["achievements"]:
                ach_selection_icons["achievements"][achievement["name"]]["icon"] = achievement["icon"]
        return ach_selection_icons
    else:
        return ach_selection
"""

if __name__ == "__main__":
    from flask_cors import CORS
    CORS(app)
    app.run()
