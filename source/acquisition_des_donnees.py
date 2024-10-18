#!/usr/bin/env python
# coding: utf-8

# # Part 1: Acquisition de données
# 
# #### Logique générale
# 1. Classe pour téléchargement de données
# 2. Téléchargement des matches de 2016 à 2023:
#     * **Saisons régulières**. Sauvegarde dans: _data/nhl_reguliere_
#     * **Matches des playoffs**. Sauvegarde dans: _data/nhl_playoffs_
# 3. Fusion des deux repertoires _data/nhl_reguliere_ et _data/nhl_playoffs_ dans _data/nhl_data_

# ### 1. Classe pour téléchargement de données

# In[14]:


import os
import requests
import json
import time

class NHLDataDownloader:
    def __init__(self, base_dir):
        """
        Initialise le répertoire où les données seront sauvegardées.
        :param base_dir: Chemin du répertoire local pour la sauvegarde des données
        """
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def download_game_data(self, game_id: str) -> dict:
     """
    Télécharge les données d'un match spécifique depuis l'API de la LNH.
    Si le fichier existe déjà localement, il est chargé depuis le disque.
    :param game_id: L'identifiant unique du match (ex. '2020020001' pour le premier match de la saison 2020-21)
    :return: Un dictionnaire contenant les données du match, ou None en cas d'erreur
    """
     file_path = os.path.join(self.base_dir, f"{game_id}.json")
     if os.path.exists(file_path):
        print(f"Fichier {game_id}.json déjà existant dans le répertoire {self.base_dir}.")
        with open(file_path, 'r', encoding='utf-8') as f:
                game = json.load(f)
                return game
     else:
        game_type = str(game_id)[4:6]
        game = None  # Initialisation de la variable 'game'
        if game_type == '02' or game_type == '03':
            url = f"https://api-web.nhle.com/v1/gamecenter/{str(game_id)}/play-by-play"
            try:
                response = requests.get(url)
                response.raise_for_status()  # Vérifie si la requête a réussi
                game = response.json()
                with open(os.path.join(self.base_dir, f"{game_id}.json"), 'w', encoding='utf-8') as f:
                    json.dump(game, f, ensure_ascii=False, indent=4)
                    f.close()
                    print(f"Téléchargé et enregistré : {game_id}.json")
            except Exception as e:
                print(f"Erreur de téléchargement du match {game_id}: {e}")
            time.sleep(1)  # Délai d'une seconde entre les requêtes
        return game                        


# ##### Exemple de téléchargement d'un fichier existent et d'un fichier non-existent

# In[2]:


# Utilisation de la classe
downloader = NHLDataDownloader(base_dir='../data/test')

# Télécharge les données pour la saison 2016 (saison régulière et playoffs)
downloader.download_game_data(2016020001)
downloader.download_game_data(2016020002)


# ### 2. Téléchargement des matches de 2016 à 2023

# #### **Saisons régulières**. Sauvegarde dans: _data/nhl_reguliere_

# In[10]:


# Utilisation de la classe
downloader = NHLDataDownloader(base_dir='../data/nhl_reguliere')

def download_all_seasons(downloader, start_year, end_year):    
    # Cette partie a seulement relation avec la saison régulière (type 2) 
    """
    Télécharge les données pour des saisons de la LNH.
    :param downloader: Une instance de la classe NHLDataDownloader
    :param year: Année de début de la saison (ex. '2020')
    :param no_of_games: Nombre de matchs à télécharger pour la saison régulière (ex. 1271)
    :param game_type: '02' pour la saison régulière
    """

    for year in range(start_year, end_year + 1):
        year_str = str(year)
        downloaded_count = 0
        
        # Définir le nombre de matchs en fonction de l'année
        if year_str == '2016':
            no_of_games = 1231  # 1230 matches in 2016
        elif year_str == '2020':
            no_of_games = 869  # 868 matches in 2020 because of covid
        elif year_str in ['2017', '2018', '2019']:
            no_of_games = 1272  # Matches normaux pour ces années
        else:
            no_of_games = 1354  # Pour les années 2021 et après (32 équipes)

        #print(f"Téléchargement des données de la saison {year_str} pour {no_of_games} matchs.")

        # Boucler sur les IDs de match pour télécharger les données de la saison régulière (type 02)
        for game_number in range(1, no_of_games + 1):
            game_id = f"{year_str}02{str(game_number).zfill(4)}"  # Format de l'ID de jeu
            game_data = downloader.download_game_data(game_id=game_id)

            #Vérifier le contenu des données téléchargées
            if game_data:
                downloaded_count += 1
                #print(f"Données pour le game_id {game_id} téléchargées avec succès.")
            #else:
                #print(f"Aucune donnée disponible pour le game_id {game_id}.")
        print(f"Total de fichiers téléchargés pour la saison {year_str}: {downloaded_count}")


# In[ ]:


# Télécharger toutes les saisons de 2016 à 2023
download_all_seasons(downloader, start_year=2016, end_year=2023)


# #### **Playoffs**. Sauvegarde dans: _data/nhl_playoffs_

# In[5]:


# Utilisation de la classe
downloader = NHLDataDownloader(base_dir='../data/nhl_playoffs')

def download_playoffs_data(downloader,start_year, end_year) -> None:
    """
        Fonction utilisant des appels REST calls pour télécharger les données des playoffs des saisons allant de start_year à end_year. Sauvegarde le résultat json dans le path 
        défini dans la classe NHLDataDownloader
        :param start_year: année de début de la liste écrite en 4-digits.
        :param end_year: année de fin de la liste écrite en 4-digits.
        :return: None

        """
    #Premier tour des playoffs (1/8 de finale) : 0301
    #Deuxième tour (quarts de finale) : 0302
    #Troisième tour (demi-finales) : 0303
    #Finale : 0304
       
    for year in range(start_year, end_year + 1):
        year_str = str(year)
        print(f"Téléchargement des données des playoffs pour la saison {year_str}")

        # Générer les IDs des matchs de playoffs
        playoffs = []
        # Huitièmes de finale
        playoffs.extend([f"{year_str}0301{str(matchup)}{game_number}" for matchup in range(1, 9) for game_number in range(1, 8)])
        # Quarts de finale
        playoffs.extend([f"{year_str}0302{str(matchup)}{game_number}" for matchup in range(1, 5) for game_number in range(1, 8)])   
        # Demi-finales
        playoffs.extend([f"{year_str}0303{str(matchup)}{game_number}" for matchup in range(1, 3) for game_number in range(1, 8)])   
        # Finales
        playoffs.extend([f"{year_str}0304{str(1)}{game_number}" for game_number in range(1, 8)])        
        
        # Télécharger chaque match de playoffs
        for game_id in playoffs:
            game_data = downloader.download_game_data(game_id=game_id)
            # Vérifier le contenu des données téléchargées
            if game_data:
                print(f"Données pour le game_id {game_id} téléchargées avec succès.")
            else:
                print(f"Aucune donnée disponible pour le game_id {game_id}.")

# Télécharger toutes les données des playoffs de 2016 à 2023
download_playoffs_data(downloader, start_year=2016, end_year=2023)


# ### 3. Fusion des deux repertoires
# _data/nhl_reguliere_ et _data/nhl_playoffs_ dans _data/nhl_data_

# In[4]:


import os
import shutil

# Define the paths to your folders
reguliere_folder = '../data/nhl_reguliere'
playoffs_folder = '../data/nhl_playoffs'
destination_folder ='../data/nhl_data'

# Create the destination folder if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Function to copy files from a source folder to the destination folder
def copy_files(source_folder, destination_folder):
    # Loop through all files in the source folder
    for filename in os.listdir(source_folder):
            source_file = os.path.join(source_folder, filename)
            destination_file = os.path.join(destination_folder, filename)

            # Check if the source_file is actually a file and not a directory
            if os.path.isfile(source_file):
                # Copy the file to the destination folder
                shutil.copy(source_file, destination_file)
                print(f"Copied {filename} to {destination_folder}")
            else:
                print(f"Skipped directory: {filename}")

# Copy files from both nhl_reguliere and nhl_playoffs to nhl_data
copy_files(reguliere_folder, destination_folder)
copy_files(playoffs_folder, destination_folder)

print("All files have been copied successfully.")

