import numpy as np
import pandas as pd
def compute_shot_angle(coordinate_x: float, coordinate_y: float):
    # If the shot is made on the right side
    if coordinate_x >= 0:
        x_net = 89.0
        if coordinate_x == 89.0:  # Shot perpendicular to the net
            return 90

        x_dist_abs = np.abs(coordinate_x - x_net)
        if coordinate_x > 89.0:  # Shot behind the net
            return 90 + np.rad2deg(np.arctan(coordinate_y / x_dist_abs))

        return np.rad2deg(np.arctan(coordinate_y / x_dist_abs))

    else:  # If the shot is made on the left side
        x_net = -89.0
        if coordinate_x == -89:  # Shot perpendicular to the net
            return 90

        x_dist_abs = np.abs(coordinate_x - x_net)
        if coordinate_x < -89.0:  # Shot behind the net
            return 90 + np.rad2deg(np.arctan(coordinate_y / x_dist_abs))

        return np.rad2deg(np.arctan(coordinate_y / x_dist_abs))
    


def find_net(coordinate_x : int):
    """This function returns the net where the attacking team should put the hockey puck"""
    if coordinate_x <= 0 :
        return 'left'
    else :
        return 'right'
    
def compute_distance_to_net(coordinate_x : float, coordinate_y : float):
    """This function determines the net where the attacking team shoots during the play
      and then computes the distance to the net"""
    net_side = find_net(coordinate_x)
    # Cas où le filet sur lequel l'équipe tire se trouve sur la droite
    if net_side == 'right' :
        dist = np.sqrt((coordinate_x - 89)**2 + coordinate_y**2)
    else : 
        # Cas où le filet sur lequel l'équipe tire se trouve sur la gauche
        dist = np.sqrt((coordinate_x + 89)**2 + coordinate_y**2)
    return dist

def df_add_distance_to_net(df : pd.DataFrame):
    """This function adds a column containing the distance to the net 
    to the DataFrame"""

    df['distance_to_net'] = df.apply(lambda row : compute_distance_to_net(row['x_coordinate'],
                                                row['y_coordinate']),axis = 1) 
    
    return df 