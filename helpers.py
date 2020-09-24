# helpers.py
#
# Various helper methods for loading and processing achievement data

import json
import requests
# import random


def import_list_from_file(filename):
    with open(filename, encoding="utf-8") as f:
        file_list = [line.rstrip() for line in f]
    return file_list


def import_json_to_dict(filename):
    with open(filename, encoding="utf-8") as f:
        json_str = f.read()
        new_dict = json.loads(json_str)
        return new_dict


def index_player_achievements(ach_dict):
    """
    Format player achievement data
    :param ach_dict: Dictionary. User achievement data returned from Steam API
    :return: Dictionary
    """
    new_dict = {}
    for achievement in ach_dict["playerstats"]["achievements"]:
        new_dict[achievement["apiname"]] = {
            "achieved": achievement["achieved"],
            "unlock_time": achievement["unlocktime"],
            "name": achievement["name"],
            "description": achievement["description"]
        }
    return new_dict


def get_filtered_achievements_for_user(player_dict, ref_dict):
    """
    Compare player achievements with reference, and remove all achievements which are not leader-specific and which have
    not been achieved by the player. Append a list of leaders with outstanding achievements.
    :param player_dict: User achievement data retrieved from Steam API
    :param ref_dict: Master achievement reference
    :return: Dictionary
    """
    filtered_ref_dict = {key: value for (key, value) in ref_dict.items()
                         if ref_dict[key]["leader-specific"] is True and player_dict[key]["achieved"] == 0}

    leader_list = []
    for key in filtered_ref_dict.keys():
        for leader in filtered_ref_dict[key]["leaders"]:
            if leader not in leader_list:
                leader_list.append(leader)

    user_ach_dict = {
        "leader_list": leader_list,
        "achievements": filtered_ref_dict
    }

    return user_ach_dict


def get_game_data(steam_api_key, app_id):
    """
    Retrieve achievement data from Steam API. Used to update achievement icon references on app startup.
    :param steam_api_key: String, numeric. Secret key for Steam API access
    :param app_id: String, numeric. Identifies app to Steam API.
    :return: Dictionary. Response from Steam API
    """
    game_data_url = (
        f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
        f"?key={steam_api_key}"
        f"&appid={app_id}"
    )

    r = requests.get(game_data_url)
    if r.status_code == 200:
        response_dict = r.json()
        return response_dict
    else:
        # TODO: Add error logic
        return


def build_achievement_reference(filepath, steam_api_key, app_id):
    """
    Filter achievement list to only include those achievements which are leader-specific, then append icon URIs
    :param filepath: String. Reference to text file with JSON-formatted achievement data
    :param steam_api_key: String, numeric. Secret key for Steam API access
    :param app_id: String, numeric. Identifies app to Steam API.
    :return: Dictionary.
    """
    ach_dict = import_json_to_dict(filepath)
    leaders_dict = {key: value for (key, value) in ach_dict.items() if value["leader-specific"] is True}
    game_data = get_game_data(steam_api_key, app_id)
    if game_data:
        for achievement in game_data["game"]["availableGameStats"]["achievements"]:
            if achievement["name"] in leaders_dict:
                leaders_dict[achievement["name"]]["icon"] = achievement["icon"]
    return leaders_dict


# Legacy methods for server-side random logic
"""
def get_all_achievements_for_leader(leader, ref_dict):
    # print(f"Getting all achievements for {leader}...")
    achievement_dict = {
        "leader": leader,
        "achievements": {}
    }
    for key in ref_dict.keys():
        if ref_dict[key]["leader-specific"] is True and leader in ref_dict[key]["leaders"]:
            achievement_dict["achievements"][key] = {
                "name": ref_dict[key]["name"],
                "description": ref_dict[key]["description"]
            }
    return achievement_dict


def get_random_leader_from_achievements(player_dict, ref_dict):
    # print("Getting random leader from outstanding achievements...")
    leader_list = []
    for key in ref_dict.keys():
        if ref_dict[key]["leader-specific"] is True and player_dict[key]["achieved"] == 0:
            for leader in ref_dict[key]["leaders"]:
                if leader not in leader_list:
                    leader_list.append(leader)
    random_leader = random.choice(leader_list)
    print("Leader selected: " + random_leader)
    return random_leader


def get_outstanding_achievements_by_leader(leader, player_dict, ref_dict):
    achievement_dict = {
        "leader": leader,
        "achievements": {}
    }
    for key in ref_dict.keys():
        if ref_dict[key]["leader-specific"] is True and leader in ref_dict[key]["leaders"]:
            if player_dict[key]["achieved"] == 0:
                achievement_dict["achievements"][key] = {
                    "name": ref_dict[key]["name"],
                    "description": ref_dict[key]["description"]
                }
    return achievement_dict

"""