#!/usr/bin/env python
# coding: utf-8

# # Part 5: Visualisations avancées

# In[2]:


import os, json, pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns


# In[10]:


# Charger le fichier CSV
df = pd.read_csv('nhl_play_by_play_combined.csv')

#Filter by Season
df2=df[df["season"]==20202021]
df2.info()


# ### Changement des coordonnées pour l'utilisation de la demi-patinoire:

# In[11]:


def coordinate_projected_df() -> pd.DataFrame:
    """
    Charge le fichier de données nettoyé et retourne une projection des coordonnées XY des tirs sur une demi-patinoire.
    Ajuste les coordonnées x/y et vérifie les valeurs NaN ainsi que les valeurs hors limites.
    :return: DataFrame avec les colonnes ajustées x/y.
    """
    df_new = pd.read_csv('../data/nhl_play_by_play_combined.csv')
    
    # Supprime les lignes avec des valeurs NaN dans les coordonnées originales
    df_new = df_new.dropna(subset=["coordinateX", "coordinateY"])

    # Ajuste les coordonnées x et y pour la projection sur une demi-patinoire
    df_new["x_new"] = np.where(
        df_new["coordinateX"] < 0,
        -df_new["coordinateX"],
        df_new["coordinateX"],
    )
    df_new["y_new"] = np.where(
        df_new["coordinateX"] < 0,
        -df_new["coordinateY"] + 42,
        df_new["coordinateY"] + 42,
    )

    

    return df_new

# Exécute la fonction pour tester
df_new = coordinate_projected_df()
# Vérifie la présence de valeurs NaN dans les coordonnées ajustées
x_nan = df_new["x_new"].isna()
y_nan = df_new["y_new"].isna()

if x_nan.any() or y_nan.any():
        print("Attention : Des valeurs NaN ont été trouvées dans les coordonnées ajustées.")
        print("NaN dans x_new :", df_new["x_new"][x_nan])
        print("NaN dans y_new :", df_new["y_new"][y_nan])
else:
        print("Aucune valeur NaN dans les coordonnées ajustées.")

    # Vérifie si les coordonnées ajustées sont dans les limites attendues
x_out_of_bounds = (df_new["x_new"] < 0) | (df_new["x_new"] > 100)
y_out_of_bounds = (df_new["y_new"] < 0) | (df_new["y_new"] > 85)

if x_out_of_bounds.any() or y_out_of_bounds.any():
        print("Attention : Certaines coordonnées ajustées sont hors des limites attendues.")
        print("X hors limites :", df_new["x_new"][x_out_of_bounds])
        print("Y hors limites :", df_new["y_new"][y_out_of_bounds])
else:
        print("Toutes les coordonnées ajustées sont dans les limites attendues.")


# In[12]:


def calcul_moyenne_ligue(df: pd.DataFrame, saison: int) -> float:
    """
    Calcule le nombre moyen de tirs par heure pour toute la ligue pour une saison donnée.
    
    :param df: DataFrame avec les coordonnées projetées sur une demi-patinoire
    :param saison: int représentant la saison, par exemple 20202021
    :return: np.array de forme 100x85 (plan de la demi-patinoire en XY)
    """
    
    # Filtrer le DataFrame pour la saison spécifiée
    df_saison = df[df["season"] == saison].copy()  
    
    
    # Calculer le nombre total de matchs dans la saison
    total_matchs =len(df_saison["gameId"].unique())   # Correspond au nombre d'heures
    
    # Calcul du nombre total de shots dans une saison
    n_shots = df_saison.shape[0]

    # Calculer le taux de tirs moyen par heure (hypothèse : chaque match dure une heure)
    ligue_taux_shot_moy = n_shots / (total_matchs*2)

    return ligue_taux_shot_moy


# In[15]:


moyenne_ligue_data_2017= calcul_moyenne_ligue(df_new, saison=20172018)
print("Données moyennes de la ligue pour la saison ", 2017, "  :", moyenne_ligue_data_2017)

moyenne_ligue_data_2018= calcul_moyenne_ligue(df_new, saison=20182019)
print("Données moyennes de la ligue pour la saison ", 2018, "  :", moyenne_ligue_data_2018)

moyenne_ligue_data_2019= calcul_moyenne_ligue(df_new, saison=20192020)
print("Données moyennes de la ligue pour la saison ", 2019, "  :", moyenne_ligue_data_2019)

moyenne_ligue_data_2020= calcul_moyenne_ligue(df_new, saison=20202021)
print("Données moyennes de la ligue pour la saison ", 2020, "  :", moyenne_ligue_data_2020)


# In[16]:


def calcul_moyenne_tirs_equipe(df: pd.DataFrame, saison: int, equipe: str) -> np.array:
    """
    Calcule le nombre moyen de tirs par heure pour une équipe donnée pendant une saison.
    
    :param df: DataFrame contenant les coordonnées projetées sur une demi-patinoire.
    :param saison: int représentant la saison (par exemple, 20202021).
    :param equipe: str représentant le nom de l'équipe.
    :return: np.array avec une forme de 100 x 85 (c'est-à-dire le plan XY de la demi-patinoire).
    """
    
    # Filtrer le DataFrame pour la saison et l'équipe spécifiées
    df_saison = df[df["season"] == saison].copy()
    df_equipe = df_saison[(df_saison["teamHome"] == equipe) | (df_saison["teamAway"] == equipe)].copy()
    
   
    # Calculer le nombre total de matchs joués par l'équipe dans la saison
    total_matchs_equipe = df_equipe["gameId"].nunique()

    # Calcul du nombre total de shots dans une saison
    n_shots_equipe = df_equipe.shape[0]

    # Calculer le taux de tirs moyen par heure (hypothèse : chaque match dure une heure)
    equipe_taux_shot_moy = n_shots_equipe / (total_matchs_equipe*2)


    return equipe_taux_shot_moy


# In[17]:


df_new['eventTeam'].unique()


# In[18]:


moyenne_equipe_data_2017 = calcul_moyenne_tirs_equipe(df_new, 20172018, 'Hurricanes')
print("Données moyennes de l'équipe pour la saison 2017-2018 :", moyenne_equipe_data_2017)

moyenne_equipe_data_2018 = calcul_moyenne_tirs_equipe(df_new, 20182019, 'Hurricanes')
print("Données moyennes de l'équipe pour la saison 2018-2019 :", moyenne_equipe_data_2018)

moyenne_equipe_data_2019 = calcul_moyenne_tirs_equipe(df_new, 20192020, 'Hurricanes')
print("Données moyennes de l'équipe pour la saison 2019-2020 :", moyenne_equipe_data_2019)

moyenne_equipe_data_2020 = calcul_moyenne_tirs_equipe(df_new, 20202021, 'Hurricanes')
print("Données moyennes de l'équipe pour la saison 2020-2021 :", moyenne_equipe_data_2020)


# In[19]:


from scipy.ndimage import gaussian_filter

def moyenne_tirs_par_equipe_toutes_saisons(df: pd.DataFrame, saisons: list, sigma: int = 4, seuil: float = 0.001) -> dict:
    """
    Calcule le nombre moyen de tirs par heure pour chaque équipe dans la ligue pour toutes les saisons spécifiées.

    :param df: DataFrame avec les coordonnées projetées sur une demi-patinoire.
    :param saisons: Liste des saisons d'intérêt (exemple : [20172018, 20182019, 20192020]).
    :param sigma: Paramètre du noyau Gaussien pour le lissage. Intervalle recommandé : [2,4].
    :param seuil: Différences gaussiennes inférieures ou égales au seuil sont ignorées et remplacées par None.
    :return: Dictionnaire avec les saisons contenant un autre dictionnaire par équipe avec leurs fréquences de tirs.
    """
    equipes_par_saison = {}
    frequence_tirs_par_equipe_par_saison = {}

    # Construire un dictionnaire contenant toutes les équipes uniques par saison
    for saison in saisons:
        # Obtenir toutes les équipes uniques pour une saison donnée
        equipes_par_saison[saison] = np.array(df[df['season'] == saison]['teamHome'].unique())

    # Calcul de la fréquence de tirs pour chaque saison et chaque équipe
    for saison in saisons:
        # Créer un dictionnaire pour chaque saison. Chaque dictionnaire contient les équipes et leurs fréquences de tirs.
        frequence_tirs_par_equipe_par_saison[saison] = {}
        moyenne_ligue = calcul_moyenne_ligue(df, saison)
        
        for equipe in equipes_par_saison[saison]:
            moyenne_equipe = calcul_moyenne_tirs_equipe(df, saison, equipe)
            difference_moyenne = moyenne_equipe - moyenne_ligue

            # Appliquer un lissage gaussien aux résultats
            difference_lisse = gaussian_filter(difference_moyenne, sigma=sigma)

            # Ignorer les valeurs proches de zéro pour une meilleure visualisation
            difference_lisse[np.abs(difference_lisse) <= seuil] = None

            # Enregistrer le résultat
            frequence_tirs_par_equipe_par_saison[saison][equipe] = difference_lisse

    return frequence_tirs_par_equipe_par_saison


# #### Refaire l'etude pour chaque localisation (coordinate x, coordinate y)

# In[20]:


print(df_new.columns)


# In[21]:


def moyenne_tirs_equipe_par_location(df: pd.DataFrame, saison: int, equipe: str) -> np.array:
    """
    Calcule le nombre moyen de tirs par heure pour une équipe donnée et pour chaque localisation sur la demi-patinoire pendant une saison.

    :param df: DataFrame contenant les coordonnées de tir et les informations de match.
    :param saison: Saison d'intérêt (par exemple, 20202021).
    :param equipe: Nom de l'équipe pour laquelle calculer la moyenne.
    :return: np.array de taille 100x85 avec le taux moyen de tirs par heure pour chaque localisation.
    """
    # Filtrer le DataFrame pour la saison et l'équipe spécifiées
    df_saison = df[df["season"] == saison].copy()
    df_equipe = df_saison[(df_saison["teamHome"] == equipe) | (df_saison["teamAway"] == equipe)].copy()

    # Supprimer les valeurs NaN dans les coordonnées
    df_equipe = df_equipe.dropna(subset=["coordinateX", "coordinateY"])

    # Projeter les coordonnées sur une demi-patinoire
    df_equipe["x_new"] = np.where(
        df_equipe["coordinateX"] < 0,
        -df_equipe["coordinateX"],
        df_equipe["coordinateX"],
    )
    df_equipe["y_new"] = np.where(
        df_equipe["coordinateX"] < 0,
        -df_equipe["coordinateY"] + 42,
        df_equipe["coordinateY"] + 42,
    )

    # Initialiser une matrice 100x85 pour stocker le nombre de tirs par localisation
    data_equipe = np.zeros((100, 85))

    # Calculer le nombre de tirs pour chaque localisation et remplir la matrice
    for (x, y), group in df_equipe.groupby(["x_new", "y_new"]):
        if not np.isnan(x) and not np.isnan(y):
            data_equipe[int(x), int(y)] = len(group)

    # Calculer le nombre total de matchs joués par l'équipe dans la saison
    total_matchs_equipe = df_equipe["gameId"].nunique()

    # Calculer le taux de tirs par heure (1 heure par match, hypothèse)
    data_equipe = data_equipe / total_matchs_equipe

    return data_equipe

# Exemple d'utilisation
df_new = pd.read_csv('../data/nhl_play_by_play_combined.csv')  # Charger les données
taux_moyen_tirs_location_equipe = moyenne_tirs_equipe_par_location(df_new, saison=20202021, equipe="Canadiens")
print("Matrice des tirs moyens par heure pour chaque localisation pour les Canadiens:", taux_moyen_tirs_location_equipe)


# In[22]:


def ligue_projected_array(df: pd.DataFrame, saison: int) -> np.array:
    """
    Calcule une matrice 100x85 représentant le nombre moyen de tirs par heure pour chaque localisation sur la demi-patinoire.
    
    :param df: DataFrame contenant les coordonnées de tir et les informations de match.
    :param saison: Saison d'intérêt (par exemple, 20202021).
    :return: np.array de taille 100x85 avec le taux moyen de tirs par heure pour chaque localisation.
    """
    # Filtrer le DataFrame pour la saison spécifiée
    df_saison = df[df["season"] == saison].copy()

    # Supprimer les valeurs NaN dans les coordonnées
    df_saison = df_saison.dropna(subset=["coordinateX", "coordinateY"])

    # Projeter les coordonnées sur une demi-patinoire
    df_saison["x_new"] = np.where(
        df_saison["coordinateX"] < 0,
        -df_saison["coordinateX"],
        df_saison["coordinateX"],
    )
    df_saison["y_new"] = np.where(
        df_saison["coordinateX"] < 0,
        -df_saison["coordinateY"] + 42,
        df_saison["coordinateY"] + 42,
    )

    # Initialiser une matrice 100x85 pour stocker le nombre de tirs par localisation
    data_ligue = np.zeros((100, 85))

    # Calculer le nombre de tirs pour chaque localisation et remplir la matrice
    for (x, y), group in df_saison.groupby(["x_new", "y_new"]):
        if not np.isnan(x) and not np.isnan(y):
            data_ligue[int(x), int(y)] = len(group)

    # Calculer le nombre total de matchs joués dans la saison
    total_games_ligue = df_saison["gameId"].nunique()

    print(total_games_ligue)

    # Calculer le taux de tirs par heure (1 heure par match, hypothèse)
    data_ligue = data_ligue / total_games_ligue

    return data_ligue

# Exemple d'utilisation
df_new = pd.read_csv('../data/nhl_play_by_play_combined.csv')  # Charger les données
moyenne_tirs_location = ligue_projected_array(df_new, saison=20202021)
print("Matrice des tirs moyens par heure pour chaque localisation :", moyenne_tirs_location)


# In[23]:


def moyenne_tirs_equipe_par_location(df: pd.DataFrame, saison: int, equipe: str) -> np.array:
    """
    Calcule le nombre moyen de tirs par heure pour une équipe donnée et pour chaque localisation sur la demi-patinoire pendant une saison.

    :param df: DataFrame contenant les coordonnées de tir et les informations de match.
    :param saison: Saison d'intérêt (par exemple, 20202021).
    :param equipe: Nom de l'équipe pour laquelle calculer la moyenne.
    :return: np.array de taille 100x85 avec le taux moyen de tirs par heure pour chaque localisation.
    """
    # Filtrer le DataFrame pour la saison et l'équipe spécifiées
    df_saison = df[df["season"] == saison].copy()
    df_equipe = df_saison[(df_saison["teamHome"] == equipe) | (df_saison["teamAway"] == equipe)].copy()

    # Supprimer les valeurs NaN dans les coordonnées
    df_equipe = df_equipe.dropna(subset=["coordinateX", "coordinateY"])

    # Projeter les coordonnées sur une demi-patinoire
    df_equipe["x_new"] = np.where(
        df_equipe["coordinateX"] < 0,
        -df_equipe["coordinateX"],
        df_equipe["coordinateX"],
    )
    df_equipe["y_new"] = np.where(
        df_equipe["coordinateX"] < 0,
        -df_equipe["coordinateY"] + 42,
        df_equipe["coordinateY"] + 42,
    )

    # Initialiser une matrice 100x85 pour stocker le nombre de tirs par localisation
    data_equipe = np.zeros((100, 85))

    # Calculer le nombre de tirs pour chaque localisation et remplir la matrice
    for (x, y), group in df_equipe.groupby(["x_new", "y_new"]):
        if not np.isnan(x) and not np.isnan(y):
            data_equipe[int(x), int(y)] = len(group)

    # Calculer le nombre total de matchs joués par l'équipe dans la saison
    total_matchs_equipe = df_equipe["gameId"].nunique()

    # Calculer le taux de tirs par heure (1 heure par match, hypothèse)
    data_equipe = data_equipe / total_matchs_equipe

    return data_equipe

# Exemple d'utilisation
df_new = pd.read_csv('../data/nhl_play_by_play_combined.csv')  # Charger les données
taux_moyen_tirs_location_equipe = moyenne_tirs_equipe_par_location(df_new, saison=20202021, equipe="Canadiens")
print("Matrice des tirs moyens par heure pour chaque localisation pour les Canadiens:", taux_moyen_tirs_location_equipe)


# In[24]:


def moyenne_tirs_par_equipe_toutes_saisons_loc(df: pd.DataFrame, saisons: list, sigma: int = 4, seuil: float = 0.0001) -> dict:
    """
    Calcule le nombre moyen de tirs par heure pour chaque équipe dans la ligue pour toutes les saisons spécifiées.

    :param df: DataFrame contenant les coordonnées projetées sur une demi-patinoire.
    :param saisons: Liste des saisons d'intérêt (exemple : [20172018, 20182019, 20192020]).
    :param sigma: Paramètre du noyau Gaussien pour le lissage. Intervalle recommandé : [2,4].
    :param seuil: Différences gaussiennes inférieures ou égales au seuil sont ignorées et remplacées par None.
    :return: Dictionnaire avec les saisons contenant un autre dictionnaire par équipe avec leurs fréquences de tirs.
    """
    equipes_par_saison = {}
    frequence_tirs_par_equipe_par_saison = {}

    # Récupérer les équipes uniques (domicile et extérieur) par saison sans duplications
    for saison in saisons:
        equipes_home = set(df[df['season'] == saison]['teamHome'].unique())
        equipes_away = set(df[df['season'] == saison]['teamAway'].unique())
        # Union des équipes domicile et visiteur sans duplications
        equipes_par_saison[saison] = equipes_home.union(equipes_away)
        # Afficher les équipes pour la saison
        print(f"Saison {saison}, Équipes listées : {sorted(equipes_par_saison[saison])}")

    # Calcul de la fréquence de tirs pour chaque saison et chaque équipe
    for saison in saisons:
        frequence_tirs_par_equipe_par_saison[saison] = {}
        moyenne_ligue = ligue_projected_array(df, saison)
        
        for equipe in equipes_par_saison[saison]:
            # Obtenir la fréquence moyenne des tirs pour l'équipe et la saison données
            moyenne_equipe = moyenne_tirs_equipe_par_location(df, saison, equipe)
            difference_moyenne = moyenne_equipe - moyenne_ligue

            # Appliquer un lissage gaussien aux résultats
            difference_lisse = gaussian_filter(difference_moyenne, sigma=sigma)

            # Ignorer les valeurs proches de zéro pour une meilleure visualisation
            difference_lisse[np.abs(difference_lisse) <= seuil] = None

            # Enregistrer le résultat pour l'équipe et la saison
            frequence_tirs_par_equipe_par_saison[saison][equipe] = difference_lisse

    return frequence_tirs_par_equipe_par_saison

# Exemple d'utilisation
saisons = [20172018, 20182019, 20192020, 20202021]
df_new = pd.read_csv('../data/nhl_play_by_play_combined.csv')  # Charger les données
frequence_tirs = moyenne_tirs_par_equipe_toutes_saisons_loc(df_new, saisons)

# Affichage d'un exemple pour une équipe et une saison
for saison in frequence_tirs:
    for equipe in frequence_tirs[saison]:
        print(f"Saison {saison}, Équipe {equipe}, Fréquence des tirs par localisation :")
        print(frequence_tirs[saison][equipe])


# In[26]:


from PIL import Image

# Plotly Imports
import plotly.graph_objects as go
import cufflinks as cf
from plotly.offline import download_plotlyjs, init_notebook_mode,plot, iplot
init_notebook_mode(connected=True)
cf.go_offline()


# In[27]:


RINK_IMG  = '../figures/nhl_rink.png'


# In[29]:


df_new = pd.read_csv('../data/nhl_play_by_play_combined.csv')  # Charger les données

# Définir la liste des saisons d'intérêt de 20162017 à 20202021
saisons = [20162017, 20172018, 20182019, 20192020, 20202021]

# Calculer la fréquence moyenne de tirs par équipe pour chaque saison
team_year_shoot = moyenne_tirs_par_equipe_toutes_saisons_loc(df_new, saisons)


# ### Explications des principaux éléments du graphique interactif:
# 
# - **Initialisation de l'ensemble equipes:** On utilise un ensemble pour stocker les équipes de chaque saison sans duplications. On le convertit ensuite en liste triée.
# 
# - **Matrice A de NaN:** Utilisée pour remplacer les équipes absentes dans certaines saisons, assurant une cohérence des données.
# 
# - **Création des grilles _xx_ et _yy_ :** Ces grilles définissent les coordonnées pour l'affichage des contours.
# 
# - **Configuration de _fig.add_layout_image_:** L'image de la patinoire est superposée en arrière-plan.
# 
# - **Menus déroulants:** _boutons_saisons_ et _boutons_equipes_ permettent de sélectionner la saison et l'équipe à visualiser.
# 
# Ce code génère une carte interactive des tirs pour différentes équipes et saisons, avec des options de personnalisation pour rendre le graphique plus clair et facile à naviguer.

# In[31]:


# Chemin vers l'image de la patinoire
RINK_IMG = '../figures/nhl_rink.png'

def contour(df_shoot, html_out=True):
    # Initialiser l'ensemble de toutes les équipes uniques à travers les saisons
    equipes = set()  # Utiliser un ensemble pour éviter les doublons
    
    # Parcourir chaque saison pour collecter toutes les équipes
    for saison in df_shoot.keys():
        equipes.update(df_shoot[saison].keys())
    
    equipes = sorted(equipes)  # Convertir en liste triée pour un ordre cohérent
    
    # Définir des valeurs NaN pour les équipes absentes dans certaines saisons
    A = np.ones((100, 85))  # Matrice de 100x85 pour représenter la patinoire
    A[:] = np.nan  # Remplir de NaN
    df_saisons = {}
    for saison in df_shoot.keys():
        df_saisons[saison] = {}
        for equipe in equipes:
            # Si l'équipe n'est pas présente dans la saison, lui assigner la matrice NaN
            if equipe not in df_shoot[saison].keys():
                df_shoot[saison][equipe] = A
            # Sinon, ajouter les données de l'équipe
            df_saisons[saison][equipe] = df_shoot[saison][equipe]
    
    # Créer la grille de coordonnées pour le graphique
    xx, yy = np.mgrid[0:100:100j, -42.5:42.5:85j]
    saison_initiale = df_saisons[list(df_saisons.keys())[0]]
    equipe_initiale = saison_initiale[list(saison_initiale.keys())[0]]
    
    # Initialiser la figure avec l'image de la patinoire
    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source=Image.open(RINK_IMG),
            xref="x",
            yref="y",
            x=-100,
            y=42.5,
            sizex=200,
            sizey=85,
            sizing="stretch",
            opacity=0.5,
            layer="below"
        )
    )
    
    # Ajouter des courbes de contours pour chaque équipe
    for equipe in equipes:
        fig.add_trace(
            go.Contour(
                x=xx[:, 1],
                y=yy[1, :], 
                z=np.rot90(np.fliplr(equipe_initiale)),
                colorscale='RdBu',
                reversescale=True,
                connectgaps=False,
                name=equipe,
                visible=True if equipe == equipes[0] else False  # Rendre visible uniquement la première équipe au départ
            )
        )
    
    # Configurer les menus déroulants pour sélectionner la saison et l'équipe
    boutons_saisons = []
    boutons_equipes = []

    # Créer les options de menu pour chaque saison
    for saison in df_saisons.keys():
        liste_args = [
            np.rot90(np.fliplr(df_saisons[saison][equipe])) for equipe in equipes
        ]
        boutons_saisons.append(dict(
            method='update',
            label=str(saison),
            args=[{'z': liste_args}]
        ))

    # Créer les options de menu pour chaque équipe
    visibilite_equipes = [list(b) for b in [e == 1 for e in np.eye(len(equipes))]]
    
    for i, equipe in enumerate(equipes):
        boutons_equipes.append(dict(
            method='update',
            label=equipe,
            args=[{'visible': visibilite_equipes[i]}]
        ))
    
    # Configurer la mise en page des menus déroulants
    fig.update_layout(
        updatemenus=[
            dict(buttons=boutons_saisons, direction="down", x=0.1, xanchor="left", y=1.15, yanchor="top"),
            dict(buttons=boutons_equipes, direction="down", x=0.4, xanchor="left", y=1.15, yanchor="top")
        ]
    )
    
    # Ajouter les titres et annotations
    fig.update_layout(
        title=dict(
            text="<i>Fréquence des tirs de l'équipe par rapport à la moyenne de la ligue pour la saison</i>",
            font={'size': 18},
            y=0.075,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        annotations=[
            go.layout.Annotation(text="Saison", x=0.01, xref="paper", y=1.15, yref="paper", showarrow=False),
            go.layout.Annotation(text="Équipe", x=0.36, xref="paper", y=1.15, yref="paper", showarrow=False)
        ]
    )
    
    # Afficher la figure
    fig.show()

    # Sauvegarder en HTML si nécessaire
    if html_out:
        fig.write_html(
            '../figures/Interactive_plot.html',
            default_width='90%',
            default_height="100%",
            include_plotlyjs="cdn"
        )


# In[32]:


contour(team_year_shoot)

