import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import os
import json
import pandas as pd



class NHLPlayByPlayExtractor:
    
    def __init__(self, json_file):
        # Charger le fichier JSON
        with open(json_file, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        
    
    def extract_events(self):
        events_list = []
        
        # Extraire les informations du match
        game_id = self.data.get('id')
        season = self.data.get('season')
        team_home_Id = self.data['homeTeam']['id']
        team_away_Id = self.data['awayTeam']['id']
        team_home = self.data['homeTeam']['name']['default']
        team_away = self.data['awayTeam']['name']['default']
        
        # Extraire les actions pertinentes (uniquement les tirs et les buts)
        plays = self.data.get('plays', [])
        for play in plays:
            event_type = play['typeDescKey']

            
            # Inclure uniquement les événements "Tir au but" et "But"
            if event_type in ['shot-on-goal', 'goal']:
                event_id = play.get('eventId', 'Unknown')  # Extraction de l'event_id555
                period = play['periodDescriptor']['number']
                period_time = play['timeInPeriod']
                details = play.get('details', {})
                eventTeamId=details.get('eventOwnerTeamId', None)
                coordinate_x = details.get('xCoord', None)
                coordinate_y = details.get('yCoord', None)
                event_team = team_home if eventTeamId== self.data['homeTeam']['id'] else team_away
                home_team_defending_side = play.get('homeTeamDefendingSide', None)
                zone_code = details.get('zoneCode', None)
                

                
                # Extraire la situation du champ situationCode


                # Extraction du situationCode et des informations pertinentes
                situation_code = play.get('situationCode', None)

                if situation_code:
                  away_goalie = situation_code[0]  # 1 ou 0 pour le gardien extérieur
                  away_skaters = int(situation_code[1])  # Nombre de joueurs extérieurs
                  home_skaters = int(situation_code[2])  # Nombre de joueurs à domicile
                  home_goalie = situation_code[3]  # 1 ou 0 pour le gardien à domicile

                # Calcul de empty_net
                  if eventTeamId== self.data['awayTeam']['id']:
                    # L'équipe qui effectue l'événement est l'équipe extérieure
                    if home_goalie == '1':
                       empty_net = 0  # Le gardien de l'équipe à domicile est dans son filet
                    else:
                       empty_net = 1  # Le gardien de l'équipe à domicile a quitté son filet
                  elif eventTeamId == self.data['homeTeam']['id']:
                      # L'équipe qui effectue l'événement est l'équipe à domicile
                    if away_goalie == '1':
                       empty_net = 0  # Le gardien de l'équipe extérieure est dans son filet
                    else:
                       empty_net = 1  # Le gardien de l'équipe extérieure a quitté son filet
                  else:
                      empty_net = None  # Cas non traité

               # Calcul de strength
                  if eventTeamId == self.data['awayTeam']['id']:
                  # Équipe extérieure effectue l'événement
                    if away_skaters > home_skaters:
                      strength = "PP"  # Avantage numérique (power play) pour l'équipe extérieure
                    elif away_skaters < home_skaters:
                      strength = "SH"  # Désavantage numérique (short-handed) pour l'équipe extérieure
                    else:
                      strength = "EV"  # Forces égales
                  elif eventTeamId == self.data['homeTeam']['id']:
                 # Équipe à domicile effectue l'événement
                    if home_skaters > away_skaters:
                      strength = "PP"  # Avantage numérique pour l'équipe à domicile
                    elif home_skaters < away_skaters:
                       strength = "SH"  # Désavantage numérique pour l'équipe à domicile
                    else:
                      strength = "EV"  # Forces égales
                  else:
                    strength = None  # Cas non traité
                else:
                  empty_net = None
                  strength = None

                
                # Ajouter les informations extraites à la liste des événements
                events_list.append([
                    game_id, season, team_home_Id,team_home,team_away_Id, team_away, event_id,event_type, eventTeamId,event_team,zone_code, period,
                    period_time, coordinate_x, coordinate_y, empty_net, strength
                ])
        
        
      

        # Créer un DataFrame à partir de la liste des événements
        columns = [
            'gameId', 'season', 'teamHomeId', 'teamHome', 'teamAwayId','teamAway', 'event_id','eventType','eventTeamId','eventTeam', 'zoneCode',
            'period', 'periodTime', 'coordinateX', 'coordinateY', 'emptyNet', 'strength'
        ] 

        return pd.DataFrame(events_list, columns=columns)
    
    
    
    @staticmethod
    def clean_data(folder_path):
        all_events = []  # Liste pour stocker les événements de tous les fichiers
    
        # Obtenir tous les fichiers JSON dans le répertoire
        json_files = sorted(filter(lambda x: x.endswith('.json'), os.listdir(folder_path)))
    
        for filename in json_files:
            file_path = os.path.join(folder_path, filename)
            print(f"Traitement du fichier : {file_path}")
        
            try:
                # Passer les noms des joueurs lors de la création d'une instance de NHLPlayByPlayExtractor
                extractor = NHLPlayByPlayExtractor(file_path)
                df = extractor.extract_events()
                all_events.append(df)
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {file_path} : {e}")
    
        # Combiner tous les DataFrames en un seul
        if all_events:
            final_df = pd.concat(all_events, ignore_index=True)
            return final_df
        else:
            return pd.DataFrame()  # Retourner un DataFrame vide s'il n'y a pas d'événements


json_directory_path = '../data/nhl_data/'
df2 = NHLPlayByPlayExtractor.clean_data(json_directory_path)

# Afficher le DataFrame combiné
print(df2)



import math
import pandas as pd
import numpy as np

def calcul_distance_angle(df):
   # Initialiser la liste des distances et le dictionnaire des côtés défensifs par période pour chaque ligne
    distances = []
    home_defending_side_period = {1: None, 2: None, 3: None}

    # Boucler sur chaque ligne pour calculer les distances
    for index, row in df.iterrows():
        # Initialiser la distance à None pour chaque ligne
        distance = None

        # Extraire les informations pertinentes
        x = row['coordinateX']
        y = row['coordinateY']
        event_team_id = row['eventTeamId']
        home_team_id = row['teamHomeId']
        defending_side = row.get('homeTeamDefendingSide', None)
        zone_code = row.get('zoneCode', None)
        period = row.get('period', None)
        season = row.get('season', None)

       # Initialiser la liste des distances et le dictionnaire des côtés défensifs par période
    angles = []
    home_defending_side_period = {1: None, 2: None, 3: None}
    
    # Boucler sur chaque ligne pour calculer les distances
    
    for index, row in df.iterrows():
        # Initialiser la distance à None pour chaque ligne
        angle = None

        # Extraire les informations pertinentes
        x = row['coordinateX']
        y = row['coordinateY']
        event_team_id = row['eventTeamId']
        home_team_id = row['teamHomeId']
        defending_side = row.get('homeTeamDefendingSide', None)
        zone_code = row.get('zoneCode', None)
        period = row.get('period', None)
        season = row.get('season', None)

        # Vérifier la saison et définir les conditions de calcul
        if  zone_code is not None:
            if event_team_id == home_team_id and period in home_defending_side_period:
                if home_defending_side_period[period] is None:
                    home_defending_side_period[period] = 'right' if x > 0 else 'left'
        
            if zone_code == "D":
                if x > 0:
                    distance = math.sqrt((x + 89)**2 + y**2)
                    angle = np.arctan2(y,(x+89))
                elif x < 0:
                    distance = math.sqrt((89 - x)**2 + y**2)
                    angle = np.arctan2(y,(89-x))
            elif zone_code == "O":
                if x > 0:
                    distance = math.sqrt((89 - x)**2 + y**2)
                    angle=np.arctan2(y,(89-x))
                elif x < 0:
                    distance = math.sqrt((x + 89)**2 + y**2)
                    angle= np.arctan2(y,(x+89))
            elif zone_code == "N" and period in home_defending_side_period: 
                if event_team_id == home_team_id:
                    if home_defending_side_period[period] == 'right':
                        distance = math.sqrt((x + 89)**2 + y**2)
                        angle= np.arctan2(y,(x+89))
                    elif home_defending_side_period[period] == 'left':
                        distance = math.sqrt((89 - x)**2 + y**2)
                        angle= np.arctan2(y,(89-x))
                else:
                    if home_defending_side_period[period] == 'right':
                        distance = math.sqrt((89 - x)**2 + y**2)
                        angle= np.arctan2(y,(89-x))
                    elif home_defending_side_period[period] == 'left':
                        distance = math.sqrt((x + 89)**2 + y**2)
                        angle= np.arctan2(y,(x+89))
        
        if angle is not None:
            angle = round(np.rad2deg(angle), 4)

        distances.append(distance)
        angles.append(angle)

    # Ajouter les distances calculées au DataFrame
    df['distance'] = distances
    df['distance_round'] = df['distance'].round(0)


    # Ajouter les distances calculées au DataFrame
    df['angle'] = angles
    
    return df


# Calculer les distances pour toutes les saisons
df2 = calcul_distance_angle(df2)

# Afficher le DataFrame mis à jour
print(df2.head())

# Supprimer les lignes contenant des NaN dans les colonnes 'coordinateX' ou 'coordinateY'
df2 = df2.dropna(axis=0, subset=['angle'])

# Réinitialiser l'index après suppression des lignes
df2 = df2.reset_index(drop=True)

# Afficher un message pour confirmer le nettoyage
print(f"Nettoyage terminé. Nombre de lignes restantes : {len(df2)}")

gameID=df2['gameId']
distance= df2['distance']
angle= df2['angle']
isGoal = df2['isGoal']
emptyNet = df2['emptyNet']

# Save the lists into a new dataframe
data = pd.DataFrame({'gameID': gameID,
                     'distance': distance ,
                     'angle': angle,
                     'isGoal': isGoal,
                     'emptyNet': emptyNet
                    })

# Filtrer les données où isGoal est égal à 1
data_goals = data[data['isGoal'] == 1]

# Afficher les dernières lignes de ce DataFrame filtré
print(data_goals.tail())

# Assurez-vous que 'gameID' est de type string
data['gameID'] = data['gameID'].astype(str)

# Maintenant, divisez les données en ensembles d'entraînement et de test
train_data = data[(data['gameID'].str[:4] == '2016') | 
                  (data['gameID'].str[:4] == '2017') | 
                  (data['gameID'].str[:4] == '2018') | 
                  (data['gameID'].str[:4] == '2019')]

test_data = data[data['gameID'].str[:4] == '2020']




