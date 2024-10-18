#!/usr/bin/env python
# coding: utf-8

# # Part 3: Nettoyage de donnees

# Les colonnes demandées pour la représentation des donnéees(caracteritiques) sont:
# 
# * L'heure / la période de jeu
# * L'identifiant du jeu
# * Les informations sur l'équipe _(quelle équipe a tiré)_
# * S'il s'agit d'un tir ou d'un but
# * Les coordonnées sur la glace
# * Le nom du tireur et du gardien de but
# * Le type de tir
# * Si c'était sur un filet vide
# * Si un but était à force égale en désavantage numérique ou en avantage numérique

# #### Trois champs ne sont pas directement accessibles:
# 
# 1. **Le nom du tireur et du gardien de but:** _seuls les IDs sont disponbiles directement._
#   
#  Donc il s'agira de:
#  - Collecter les Ids et via le champs _'rosterSpots'_ qui correspond aux joueurs ayant participé au match comme joueurs effectifs _(et non sur les bancs)_ dans le fichier de données JSON
#  - Faire la correspondance entre les Ids et les noms et prénoms des skieurs.
# 
# 2. **Les deux dernieres caracteristiques requises proviennent d'un même champ dans le fichier JSON, a savoir _'situationCode'_ dans _'plays'_.**
# 
# - _'situationCode'_ est composé de 4 chiffres représentent la situation selon la configuration suivante:
#     - _Away goalie_ et _home goalie_: Pour l'état des filets des équipes away et home.
#         - Etat du filet: correspond à deux etats :
#           - **1**: _Occupé_
#           - **0**: _Vide_
#     - _Away skaters-home skaters_: Pour le nombre des skieurs des équipes away et home en confrontation.
# 
# > **Exemple 1541**: Avantage numérique pour l'équipe extérieure
# >   _(il y a 5 joueurs extérieurs et 4 joueurs à domicile sur la glace, et les deux gardiens sont toujours dans leurs filets)._

# In[1]:


import os, json, pandas as pd


# In[2]:


def extract_player_names(file_path):
    """
    Create a dictionary mapping player IDs to player names from 'rosterSpots'.
    """
    players = {}
    
    # Open the JSON file with utf-8 encoding to avoid Unicode errors
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Check if 'rosterSpots' exists in the data
        if 'rosterSpots' in data:
            for player in data['rosterSpots']:
                player_id = player['playerId']
                first_name = player['firstName']['default']
                last_name = player['lastName']['default']
                player_name = f"{first_name} {last_name}"
                players[player_id] = player_name
    except UnicodeDecodeError as e:
        print(f"Error decoding file {file_path}: {e}")
    
    return players

def process_all_files(directory):
    """
    Process all JSON files in the specified directory and extract player names.
    """
    all_players = {}
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            print(f"Processing file: {file_path}")
            player_names = extract_player_names(file_path)
            all_players.update(player_names)
    return all_players

# Example usage
nhl_data_directory = '../data/nhl_data'
all_player_names = process_all_files(nhl_data_directory)
print("Extracted Player Names:")
for player_id, player_name in all_player_names.items():
    print(f"Player ID: {player_id}, Player Name: {player_name}")


# #### Pour choisir les events goal et shot je veux d'abord savoir quel types de events j'ai

# In[3]:


def extract_unique_event_types_from_folder(folder_path):
    event_types = set()  # Utiliser un set pour obtenir des types uniques

    # Obtenir tous les fichiers JSON dans le répertoire
    json_files = sorted(filter(lambda x: x.endswith('.json'), os.listdir(folder_path)))
    
    for filename in json_files:
        file_path = os.path.join(folder_path, filename)
        print(f"Processing file: {file_path}")
        
        try:
            # Charger le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Extraire les types d'événements du champ 'plays'
            plays = data.get('plays', [])
            for play in plays:
                event_type = play.get('typeDescKey')
                if event_type:
                    event_types.add(event_type)  # Ajouter le type d'événement au set (uniquement les valeurs uniques)
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    # Retourner la liste des types d'événements uniques
    return sorted(event_types)

# Exemple d'utilisation
folder_path = '../data/nhl_data'
unique_event_types = extract_unique_event_types_from_folder(folder_path)

# Afficher la liste des types d'événements uniques
print("Types d'événements uniques dans tous les fichiers JSON :")
print(unique_event_types)


# #### Les eventtypes sont:
# 
# _['blocked-shot', 'delayed-penalty', 'faceoff', 'failed-shot-attempt', 'game-end', 'giveaway', 'goal', 'hit', 'missed-shot', 'penalty', 'period-end', 'period-start', 'shootout-complete', 'shot-on-goal', 'stoppage', 'takeaway']_
# 
# Donc ce qui est demandé est **goal** et **shot_on_goal**

# In[4]:


# Process_all_files est une fonction qui traite tous les fichiers dans le répertoire nhl_data_directory et extrait les noms des joueurs
nhl_data_directory = '../data/nhl_data' 
all_player_names = process_all_files(nhl_data_directory)

class NHLPlayByPlayExtractor:
    
    def __init__(self, json_file, player_names):
        # Charger le fichier JSON
        with open(json_file, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.player_names = player_names  # Stocker le dictionnaire des noms des joueurs
    
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
            
        
          
                # Récupérer les IDs des joueurs
                shooter_id = play['details'].get('shootingPlayerId', 'Unknown')
                goalie_id = play['details'].get('goalieInNetId', 'Unknown')
                
                # Remplacer les IDs par les noms à l'aide du dictionnaire player_names
                shooter_name = self.player_names.get(shooter_id, 'Unknown')
                goalie_name = self.player_names.get(goalie_id, 'Unknown')
                
                shot_type = play['details'].get('shotType', None)
                
                # Extraire la situation du champ situationCode


                # Extraction du situationCode et des informations pertinentes
                situation_code = play.get('details', {}).get('situationCode', None)

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
                    game_id, season, team_home_Id,team_home,team_away_Id, team_away, event_id,event_type, eventTeamId,event_team, period,
                    period_time, coordinate_x, coordinate_y, shooter_name, goalie_name, 
                    shot_type, empty_net, strength
                ])
        
        # Créer un DataFrame à partir de la liste des événements
        columns = [
            'gameId', 'season', 'teamHomeId', 'teamHome', 'teamAwayId','teamAway', 'event_id','eventType','eventTeamId','eventTeam',
            'period', 'periodTime', 'coordinateX', 'coordinateY', 'shooterName', 
            'goalieName', 'shotType', 'emptyNet', 'strength'
        ]
        return pd.DataFrame(events_list, columns=columns)
    
    
    @staticmethod
    def clean_data(folder_path, player_names):
        all_events = []  # Liste pour stocker les événements de tous les fichiers
    
        # Obtenir tous les fichiers JSON dans le répertoire
        json_files = sorted(filter(lambda x: x.endswith('.json'), os.listdir(folder_path)))
    
        for filename in json_files:
            file_path = os.path.join(folder_path, filename)
            print(f"Traitement du fichier : {file_path}")
        
            try:
                # Passer les noms des joueurs lors de la création d'une instance de NHLPlayByPlayExtractor
                extractor = NHLPlayByPlayExtractor(file_path, player_names)
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


json_directory_path = '../data/nhl_data'
df_combined = NHLPlayByPlayExtractor.clean_data(json_directory_path, all_player_names)

# Afficher le DataFrame combiné
print(df_combined)

# Enregistrer éventuellement dans un fichier CSV
df_combined.to_csv('../data/nhl_play_by_play_combined.csv', index=False) 


# #### Verifier les 10 premieres lignes du dataframe des données nettoyées:

# In[5]:


# Afficher les 10 premières lignes du DataFrame
print(df_combined.head(10))

