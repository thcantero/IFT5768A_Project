#!/usr/bin/env python
# coding: utf-8

# # Part 2: Deboggeur interactif

# ## Logique générale du déboggeur:
# 
# _Le code implémente un débogueur interactif qui comporte une interface permettant de naviguer dans différents événements, saisons et types de jeux._
# 
# ### 1. Initialisation des variables **(`__init__`)** :
#    * Le debébogueur est instancié
#    * Les données du jeu sont chargées
#    * Certaines variables sont définies pour gérer les informations sur la saison:
#         * Le type de jeu: _saison régulière ou playoffs_
#         * L'ID du jeu
#         * L'événement en cours
#    * Les widgets _(curseurs, boutons de bascule, etc.)_ sont initialisés pour permettre à l'utilisateur de sélectionner:
#        *  La saison
#        *  Le type de jeu
#        *  L'ID du match
#        *  L'événement spécifique à afficher.
# 
# 
# ### 2. Widgets interactifs:
# * Slider de saison: _Permet de sélectionner la saison à explorer._
# * Boutons de bascule: _Permettent de basculer entre les matchs de la saison régulière et les matchs des playoffs._
# * Slider d'ID de match: _Permet de sélectionner un match spécifique dans la saison._
# * Slider d'événement: _Permet de parcourir les événements d'un match. Par exemple: tirs, face-offs, buts)._
# 
# ### 3. Fonction **season_range()**:
# * Cette fonction parcourt les fichiers JSON du répertoire pour déterminer la saison minimale et maximale disponibles dans les données.
# * Renvoie une plage de saisons permettant d'ajuster dynamiquement le slider de saison.
# 
# 
# ### 4. Affichage des coordonnées de l'événement **(plot_coordinates())**:
# Affiche les coordonnées d'un événement (par exemple, un tir) sur une image d'une patinoire, si les coordonnées sont disponibles. Utilise matplotlib pour superposer les coordonnées sur l'image de la patinoire.
# 
# 
# ### 5. Affichage des informations du jeu et de l'événement **(display_info())**:
# Affiche des détails tels que l'ID du match, les équipes participantes, la date du match, le score final, le nombre d'événements et la description de l'événement actuel.
# Inclut également le nom du stade et la ville où se déroule le match, ainsi que des détails sur l'événement (période, temps écoulé).
# 
# ### 6. Filtrage des données **filter_season()** et **filter_playoffs()**:
# 
# * filter_season(): _Filtre les jeux en fonction de la saison sélectionnée par l'utilisateur._
# * filter_playoffs(): _Filtre les jeux en fonction du type de jeu sélectionné (saison régulière ou playoffs)._
# 
# ### 7. Mise à jour des variables du jeu et de l'événement **update_vars()**:
# Met à jour les variables qui contiennent des informations sur le jeu en cours et l'événement sélectionné.
# Cela inclut la mise à jour des informations sur les équipes, le score, le stade, la ville, les coordonnées de l'événement, la description, et d'autres détails pertinents.
# 
# ### 8. Mise à jour dynamique via widgets **update`_*`()**:
# Ces fonctions sont déclenchées à chaque fois que l'utilisateur modifie un widget. Elles mettent à jour la saison, le type de jeu, l'ID du jeu ou l'événement, et actualisent les informations affichées :
# * update_season(): _Met à jour les jeux en fonction de la saison choisie._
# * update_game_type(): _Met à jour les jeux en fonction du type de jeu (Playoffs ou Saison régulière)._
# * update_game_id(): _Met à jour les informations pour l'ID du jeu sélectionné._
# * update_event(): _Met à jour les informations pour l'événement sélectionné dans le jeu._
# 
# 
# ### 9. Affichage final **display_output()**:
# La fonction display_output() permet de rendre visible le widget interactif, en affichant toutes les informations mises à jour en fonction des sélections faites par l'utilisateur.

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

# Imports for JupyterLite
try:
    import piplite
    await piplite.install(['ipywidgets'])
except ImportError:
    pass
import ipywidgets as widgets
from IPython.display import display


# In[2]:


def read_files_json(folder):
    # Créer un dictionnaire pour stocker les données de tous les fichiers
    all_data = {}
    # Liste pour suivre les fichiers qui ont été lus
    files_read = []

    # Parcourir tous les fichiers dans le dossier spécifié
    for filename in os.listdir(folder):
        # Vérifier si le fichier a l'extension '.json'
        is_json = filename.endswith('.json')
        # Enlever l'extension '.json' pour obtenir le nom de base du fichier
        name = filename.replace('.json', '')
        
        if is_json:
            # Ouvrir et charger le fichier avec encodage utf-8
            try:
                with open(f"{folder}{filename}", encoding='utf-8') as file:
                    # Charger le contenu JSON du fichier dans un dictionnaire
                    file_dict = json.load(file)
                    # Ajouter le nom du fichier à la liste des fichiers lus
                    files_read.append(name)
                    # Ajouter les données du fichier au dictionnaire, avec le nom du fichier comme clé
                    all_data[name] = file_dict
            except UnicodeDecodeError as e:
                # Afficher un message d'erreur si un problème d'encodage se produit
                print(f"Erreur de décodage du fichier {filename}: {e}")
    
    # Afficher la liste des fichiers qui ont été lus avec succès
    #print(f"Fichiers lus : {files_read}")
    return all_data

# Charger toutes les données des fichiers JSON dans le dossier 'data/nhl_data/'
data = read_files_json('../data/nhl_data/')

# Charger l'image de la patinoire pour l'affichage des événements
rink = plt.imread("../figures/nhl_rink.png")


# In[3]:


# Afficher les clés principales dans 'data'
print("Clés principales dans data :", list(data.keys()))

# Afficher les premières parties d'un fichier spécifique (par exemple, le premier fichier lu dans la variable 'data'):
first_key = list(data.keys())[0]
print(f"Contenu partiel du fichier '{first_key}' :")
print(data[first_key])

# Parcourir plusieurs fichiers et afficher certains éléments
for file_key in list(data.keys())[:3]:  # Limitez l'affichage à 3 fichiers pour éviter de trop de sorties
    print(f"Contenu du fichier '{file_key}':")
    print(data[file_key], "\n")  # Affichez le contenu complet ou limitez à des parties spécifiques selon vos besoins


# Une remarque pour l'extraction du time pour l'heure de démarrage du match
# Ce temps est disponible dans le champ startTimeUTC	"2024-02-11T00:00:00Z" du ficier json sauvegardé.
# Le format T00:00:00Z fait partie de la norme ISO 8601, qui est utilisée pour représenter des dates et des heures dans un format standardisé à l'échelle internationale.
# 
# T :
# Le caractère T est utilisé comme séparateur entre la date et l'heure. Par exemple, dans la chaîne 2024-02-11T00:00:00Z, la partie avant le T (2024-02-11) représente la date (11 février 2024), et la partie après le T (00:00:00) représente l'heure.
# 
# 00:00:00 :
# Représente l'heure sous le format heures:minutes. Ici, 00:00:00 signifie minuit ou 00h00 (minuit, pile).
# 
# Z :
# Le Z à la fin est une indication du fuseau horaire. Plus précisément, le Z signifie que l'heure est exprimée en temps universel coordonné (UTC), aussi appelé Zulu Time.
# En pratique, cela signifie que l'heure indiquée (00:00:00) correspond à 00h00 UTC.
# Donc: 
# Date : 11 février 2024.
# Heure:  T00:00:00Z signifie minuit (00h00) en temps universel coordonné (UTC).

# In[4]:


class Debugger_interactif:
    def __init__(self, data):
        # Initialisation des variables
        self.data = data
        
        # Variables principales
        self.current_data = data  # Contient le dictionnaire des données actuelles (peut être filtré)
        self.current_season = str('2016')  # Saison actuelle
        self.current_game_type = 'Saison régulière'  # Type de jeu actuel (saison régulière ou playoffs)
        self.current_game_id = '2016020122'  # Match actuel (initialisé au premier)
        self.current_event = 1  # Événement actuel

        # Variables descriptives utilisées pour décrire l'événement
        self.update_vars()  # Initialisation des variables liées au jeu

        # Widgets
        self.output = widgets.Output()  # Contrôle la sortie

        # Slider pour sélectionner la saison
        self.season = widgets.IntSlider(
            value=int(self.season_range()[0]),
            min=int(self.season_range()[0]),
            max=int(self.season_range()[1]),
            description="Saison"
        )
        self.season.observe(self.update_season, 'value')

        # Boutons pour basculer entre saison régulière et playoffs
        self.game_type = widgets.ToggleButtons(options=['Saison régulière', 'Playoffs'])
        self.game_type.observe(self.update_game_type, 'value')

        # Slider pour sélectionner un match particulier
        self.game_id = widgets.SelectionSlider(
            options=sorted(list(self.current_data.keys())),
            value=self.current_game_id,
            description='ID de match',
        )
        self.game_id.observe(self.update_game_id, 'value')

        # Slider pour sélectionner un événement particulier
        self.event = widgets.IntSlider(
            value=1,
            min=1,
            max=len(self.current_data[self.current_game_id]['plays']),
            description='Événement'
        )
        self.event.observe(self.update_event, 'value')

    def season_range(self):
        """Liste les fichiers dans le dossier 'data' et renvoie la saison minimale et maximale."""
        min_season = 3000
        max_season = 0
        for game_id in self.data.keys():
            season = int(game_id[:4])
            if season < min_season:
                min_season = season
            if season > max_season:
                max_season = season
        return (str(min_season), str(max_season))

    def plot_coordinates(self):
        """Affiche les coordonnées de l'événement sur l'image de la patinoire."""
        if self.x_coordinates is not None and self.y_coordinates is not None:
            rink = plt.imread("../figures/nhl_rink.png")  # Remplacez par le bon chemin d'image
            plt.imshow(rink, zorder=0, extent=[-100, 100, -42.5, 42.5])
            plt.scatter(self.x_coordinates, self.y_coordinates, zorder=1, c='blue', marker='o', s=100)
            plt.title(self.event_time, fontsize=10)
            plt.suptitle(self.event_description, fontsize=16, y=.90)
            plt.xlabel('feet')
            plt.ylabel('feet')
            plt.show()

    def display_info(self):
        """Affiche les informations sur le match et l'événement sélectionnés."""
        with self.output:
            self.output.clear_output()  # Efface les sorties précédentes
            if self.current_game_id:
                print(f"ID de match : {self.current_game_id}")
                print(f"Numéro de match : {self.current_game_id[-4:].lstrip('0')}")
                print(f"{self.home_team} (domicile) vs. {self.away_team} (extérieur)")
                print(f"Début du match : {self.start_time}")
                print(f"Score final : {self.home_team} {self.final_score_home} - {self.final_score_away} {self.away_team}")
                print(f"Nombre total d'événements : {len(self.current_data[self.current_game_id]['plays'])}")
                print(f"Stade : {self.venue_name}, Lieu : {self.venue_city}")
                print(f"Description de l'événement actuel : {self.event_description}")
                print(f"Période : {self.event_period}, Temps dans la période : {self.event_time}")
                self.plot_coordinates()
                print("Détails de l'événement :")
                print(self.about_event)
            else:
                print("Aucune donnée disponible.")

    def filter_season(self):
        """Filtre les données selon la saison sélectionnée."""
        filtered_data = {game_id: data for game_id, data in self.data.items() if game_id.startswith(self.current_season)}
        self.current_data = filtered_data if filtered_data else self.data

    def filter_playoffs(self):
        """Filtre les données pour ne garder que les matchs de playoffs ou de saison régulière."""
        filtered_data = {}
        for game_id in self.current_data.keys():
            if self.current_game_type == "Playoffs" and game_id[4:6] == '03':
                filtered_data[game_id] = self.current_data[game_id]
            elif self.current_game_type == "Saison régulière" and game_id[4:6] == '02':
                filtered_data[game_id] = self.current_data[game_id]
        self.current_data = filtered_data

    def update_vars(self):
        """Met à jour les variables liées au jeu et à l'événement."""
        if not self.current_game_id:
            return
        game = self.current_data.get(self.current_game_id, {})
        self.home_team = game.get('homeTeam', {}).get('abbrev', 'N/A')
        self.away_team = game.get('awayTeam', {}).get('abbrev', 'N/A')
        
        # Extraction de l'heure de début du match, et récupération de la partie "T00:00:00Z"
        start_time_full = game.get('startTimeUTC', 'Inconnue')
        self.start_time = start_time_full.split('T')[-1] if 'T' in start_time_full else 'Inconnue'


        self.final_score_away = game.get('summary', {}).get('linescore', {}).get('totals', {}).get('away', 'N/A')
        self.final_score_home = game.get('summary', {}).get('linescore', {}).get('totals', {}).get('home', 'N/A')
       # Extraction des informations du stade et de la ville
        self.venue_name = game.get('venue', {}).get('default', 'Stade inconnu')
        self.venue_city = game.get('venueLocation', {}).get('default', 'Ville inconnue')


        event_details = game['plays'][self.current_event].get('details', {})
        self.x_coordinates = event_details.get('xCoord', None)
        self.y_coordinates = event_details.get('yCoord', None)
        self.event_description = game['plays'][self.current_event].get('typeDescKey', 'Aucune description')
        self.event_time = game['plays'][self.current_event].get('timeInPeriod', 'Temps inconnu')
        self.event_period = game['plays'][self.current_event].get('periodDescriptor', {}).get('number', 'Période inconnue')
        self.about_event = game['plays'][self.current_event]

    def update_season(self, x):
        """Met à jour la saison en fonction du choix de l'utilisateur."""
        self.output.clear_output()
        with self.output:
            self.current_season = str(x.new)
            self.filter_season()
            self.filter_playoffs()
            if self.current_game_id:
                self.game_id.options = sorted(list(self.current_data.keys()))
                self.update_vars()
                self.display_info()

    def update_game_type(self, x):
        """Met à jour le type de jeu en fonction de la sélection (Playoffs ou Saison régulière)."""
        self.output.clear_output()
        with self.output:
            self.current_game_type = x.new
            self.filter_season()
            self.filter_playoffs()
            if self.current_game_id:
                self.game_id.options = sorted(list(self.current_data.keys()))
                self.update_vars()
                self.display_info()

    def update_game_id(self, x):
        """Met à jour l'ID de jeu en fonction de la sélection."""
        self.current_game_id = x.new
        self.update_vars()
        self.display_info()

    def update_event(self, x):
        """Met à jour l'événement en fonction de la sélection."""
        self.current_event = x.new
        self.update_vars()
        self.display_info()

    def display_output(self):
        """Affiche le contenu de l'outil interactif."""
        display(self.output)


# In[5]:


d = Debugger_interactif(data)
display(d.season)
display(d.game_type)
display(d.game_id)
display(d.event)
d.display_output()

