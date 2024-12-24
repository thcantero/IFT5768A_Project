import argparse
import os.path
from tqdm import tqdm
import numpy as np
import pandas as pd

def get_game_seconds(period : int, period_time : object):
    minutes, seconds = map(int, period_time.split(':'))
    return (period-1)*1200 + minutes*60 + seconds


def safe_get(dct, keys, default=np.nan):
    """
    Safely get nested keys from a dictionary, return default if any key is not found.
    :param dct: dictionary to extract data from
    :param keys: dictionary keys to retrieve data
    :param default: return if any key is not found
    :return:
    """
    # Reference https://stackoverflow.com/questions/25833613/safe-method-to-get-value-of-nested-dictionary
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, TypeError):
            return default
    return dct


def clean_row(row):
    """
    Extract all shot and goal plays data from a row
    :param row: row to extract play data frame, should contain all data of a game, extracted using
    the community NHL API
    :return: dictionary containing data about all plays in one game
    """
    plays = []
    all_plays_list = row['liveData']['plays']['allPlays']
    boxscore = row['gameData']
    home_team = safe_get(boxscore, ['teams', 'home', 'name'])

    # Last event related variables
    last_event_type = np.nan
    last_x = np.nan
    last_y = np.nan
    last_period = np.nan
    last_period_time = "00:00"

    # Powerplay related variables
    home_players = 5
    away_players = 5
    powerplay_duration = 0
    penalties = []
    
    for play in all_plays_list:
        play_time = get_game_seconds(safe_get(play, ['about', 'period']), safe_get(play, ['about', 'periodTime']))

        # For each penalty, we check if the end time of the penalty is less than or equal to the current time; 
        # this would mean that the penalty has expired, so we remove it from the list. 
        for i in range(len(penalties) - 1, -1, -1):  # Iterate in reverse order, to avoid index problems when using pop()
            if penalties[i]['end'] <= play_time:
                if penalties[i]['team'] == home_team:
                    home_players += 1
                else:
                    away_players += 1
                penalties.pop(i)


        # Update powerplay timer 
        if home_players != away_players:
            powerplay_duration += play_time - get_game_seconds(last_period, last_period_time)
        else:
            powerplay_duration = 0


        # Check if event is penalty : When the event is a penalty, we add the penalty to the list and decrement the number
        # of non-goalkeeper players on the penalized team by 1. 
        if play['result']['event'] == 'Penalty':
            penalty =  {'end': play_time+ 60*play['result']['penaltyMinutes'],
                       'team': play['team']['name']}
            if penalty['team']==home_team:
                home_players -= 1
            else:
                away_players -= 1
            penalties.append(penalty)

        # Check if event is shot or goal
        if (play['result']['event'] in ['Shot', 'Goal']):
            x_coord = safe_get(play, ['coordinates', 'x'])
            y_coord = safe_get(play, ['coordinates', 'y'])
            period = safe_get(play, ['about', 'period'])
            period_time = safe_get(play, ['about', 'periodTime'])
            distance = ((x_coord-last_x)**2 + (y_coord-last_y)**2)**(1/2)
            time_elapsed = get_game_seconds(period, period_time) - get_game_seconds(last_period, last_period_time)        
            play_data = {
                'period': period,
                'period_type': safe_get(play, ['about', 'periodType']),
                'period_time': period_time,
                'game_seconds': play_time,
                'gameID': safe_get(row, ['gamePk']),
                'attacking_team_id': safe_get(play, ['team', 'id']),
                'attacking_team_name': safe_get(play, ['team', 'name']),
                'home_team':safe_get(boxscore, ['teams', 'home', 'name']),
                'play_type': safe_get(play, ['result', 'event']),
                # Reference https://www.w3schools.com/python/ref_func_next.asp
                'shooter': next((player['player']['fullName'] for player in play.get('players', [])
                                 if player['playerType'] in ['Scorer', 'Shooter']), np.NaN),
                'goalie': next((player['player']['fullName'] for player in play.get('players', [])
                                if player['playerType'] == 'Goalie'), np.NaN),
                'shot_type': safe_get(play, ['result', 'secondaryType']),
                'x_coordinate': x_coord,
                'y_coordinate': y_coord,
                'empty_net': safe_get(play, ['result', 'emptyNet']),
                'strength': safe_get(play, ['result', 'strength', 'name']),
                'last_event_type': last_event_type,
                'last_event_x': last_x,
                'last_event_y': last_y,
                'time_since_last_event': time_elapsed,
                'distance_from_last_event': distance,
                'powerplay_duration': powerplay_duration,
                'home_team_players': home_players,
                'away_team_players': away_players
            }
            plays.append(play_data)

        # Update last event details to use in next iteration
        last_event_type = safe_get(play, ["result", "event"])
        last_x = safe_get(play, ["coordinates", "x"])
        last_y = safe_get(play, ["coordinates", "y"])
        last_period = safe_get(play, ["about", "period"])
        last_period_time = safe_get(play, ["about", "periodTime"])

    return plays


def clean_json(input_dir, output_dir=""):
    """
    Get clean data from raw NHL stats API
    :param input_dir: json file to clean data from, raw data
    :param output_dir: csv file to store clean data in
    :return: pandas dataframe containing the clean data
    """
    if os.path.exists(output_dir):
        return pd.read_csv(output_dir)
    if output_dir == "":
        output_dir = input_dir.replace("json", "csv")

    df = pd.read_json(input_dir)
    tqdm.pandas()
    # Reference :https://stackoverflow.com/questions/18603270/progress-indicator-during-pandas-operations
    extracted_data = df.progress_apply(clean_row, axis=1)
    all_plays_list = [play for sublist in extracted_data for play in sublist]
    all_plays_df = pd.DataFrame(all_plays_list)

    all_plays_df.to_csv(output_dir, index=False)

    return all_plays_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Reference: https://stackoverflow.com/questions/4480075/argparse-optional-positional-arguments
    parser.add_argument("infile", type=str)
    parser.add_argument("outfile", type=str, nargs="?", default="")
    args = parser.parse_args()

    clean_json(args.infile, args.outfile)
