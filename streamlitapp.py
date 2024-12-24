import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime
from src.client.game_client import *
from src.client.serving_client import *
from src.features.ms3_clean import print_data
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


"""
General template for your streamlit app. 
Feel free to experiment with layout and adding functionality!
Just make sure that the required functionality is included as well
"""
gc = GameClient(ip="serving")
#gc = GameClient(ip="localhost")
sclient = ServingClient(ip="serving")
#sclient = ServingClient(ip="localhost")
st.title("NHL GAME")
# Displaying the NHL Logo
col1, col2, col3 = st.columns(3)
with col1:
    st.write(" ")

with col2:
    img = Image.open("figures/NHL_logo.jpeg")
    img = img.resize((img.width // 6, img.height // 6))
    st.image(img)

with col3:
    st.write(" ")

# Title of the App
st.markdown(
    "<h1 style='text-align: center; color: black;'>Hockey Visualisation App</h1>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.sidebar.title("Model selection")

    workspace = st.text_input("Workspace", "A04-Group")
    side_model = st.sidebar.selectbox(
        "Model", ("LogReg Distance", "LogReg Distance & Angle")
    )
    #version = st.text_input("Version", value="v2")

    get_model = st.button("Get Model")

    if side_model == "LogReg Distance & Angle":
        model = "expected-goal-model-angle-and-distance"
        version = "v1"
    elif side_model == "LogReg Distance":
        model = "expected-goal-distance"
        version = version= "v2"

    if get_model:
        response = sclient.download_registry_model(
            model=model, project="IFT6758.2024-A04", entity="thalia-cantero-udem", version= version
        )

        response = response["status"]

        st.markdown(
            f"<h4 style='text-align: center; color: green;'>{response}</h4>",
            unsafe_allow_html=True,
        )

user_input = st.text_input("GameID")

button = st.button("Ping game")


if button:
    if not get_model:
        response = sclient.download_registry_model(
            model=model, project="IFT6758.2024-A04", entity="thalia-cantero-udem", version= version
        )

        response = response["status"]


    gd = gc.fetch_live_game_data(user_input)

    if gd == "vide":
        st.markdown(
            f"<h2 style='text-align: center; color: black; background-color: lightcoral;'>Ce GameId n'existe pas</h2>",
            unsafe_allow_html=True,
        )
    else:
        away_team = gd["awayTeam"]["commonName"]["default"]
        home_team = gd["homeTeam"]["commonName"]["default"]

        year = int(user_input[0:4])
        gametype = user_input[4:6]
        if gametype == "01":
            g_type = "Regular season ##\n"
        elif gametype == "02":
            g_type = "All-Star ##\n"
        elif gametype == "03":
            g_type = "Playoffs ##\n"

        saisons = f"""
                ## Saison {year}/{year+1} 
                ## {g_type} """

        teams = f"{home_team} vs {away_team}"

        st.markdown(
            f"<h1 style='text-align: center; color: black;'>{saisons}</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<h3 style='text-align: center; color: black; background-color: aliceblue;'>{teams}</h3>",
            unsafe_allow_html=True,
        )

    data = print_data(gd)

    st.write(" ")
    st.write(" ")

    # st.slider("Event", len(data))

    st.markdown(
        f"<h5 style='text-align: center; color: black;'>{home_team} xG (actual)&emsp;&emsp;&emsp;&emsp;&emsp; {away_team} xG (actual)</h5>",
        unsafe_allow_html=True,
    )

    away_score = gd["awayTeam"]["score"]
    home_score = gd["homeTeam"]["score"]

    home_team_score = 0
    away_team_score = 0

    for index, row in data.iterrows():
            if row["is_goal"] == 1:
                if row["event_owner_team_id"] == row["home_team_id"]:
                    home_team_score += 1
                else:
                    away_team_score += 1
            data.at[index, "home_team_goals"] = home_team_score
            data.at[index, "away_team_goals"] = away_team_score

            # Safely access periodDescriptor
            #period_descriptor = row["periodDescriptor"]
            #period_descriptor = row.get("periodDescriptor")
            #period_number = period_descriptor.get("number")
            period_number = row["number"]
            time_remaining = row.get("timeRemaining", "00:00")
            period_time = row.get("timeInPeriod", "00:00")


            if period_number in [1, 2, 3]:
                time_in_period = datetime.strptime("20:00", "%M:%S")
                time_played_in_period = datetime.strptime(row["period_time"], "%M:%S")

                time_left = time_in_period - time_played_in_period
                minutes, seconds = divmod(time_left.seconds, 60)
                formatted_time_left = f"{minutes:02d}:{seconds:02d}"

                data.at[index, "time_left_in_period"] = formatted_time_left
            else:
                time_in_period = datetime.strptime("05:00", "%M:%S")
                time_played_in_period = datetime.strptime(row["period_time"], "%M:%S")

                time_left = time_in_period - time_played_in_period
                minutes, seconds = divmod(time_left.seconds, 60)
                formatted_time_left = f"{minutes:02d}:{seconds:02d}"

                data.at[index, "time_left_in_period"] = formatted_time_left

    features = [
        "shot_type",
        "x_coordinate",
        "y_coordinate",
        "away_team_players",
        "home_team_players",
        "empty_net",
        "distance_to_net",
        "shot_angle",
        "home_team_goals",
        "away_team_goals",
        "time_left_in_period",
        "prediction",
        ]

    df_shot = data[data["event_type"] == "shot-on-goal"]
    df_shot = df_shot.reset_index(drop=True)

    if side_model == "LogReg Distance & Angle":
        columns = ["distance_to_net", "shot_angle"]
    elif side_model == "LogReg Distance":
        columns = ["distance_to_net"]

    data = df_shot[columns].values
    df = pd.DataFrame(data, columns=columns)
    
    predictions = sclient.predict(df)

    df_shot = pd.concat([df_shot, predictions], axis=1)

    home_team_cum_prob = 0
    away_team_cum_prob = 0

    for index, row in df_shot.iterrows():
        if row["home_team_id"] == row["event_owner_team_id"]:
            home_team_cum_prob += row["prediction"]
        else:
            away_team_cum_prob += row["prediction"]

    difference_home = round(home_score - home_team_cum_prob, 2)
    difference_away = round(away_score - away_team_cum_prob, 2)

    if difference_away < 0:
        fleche_away = "↓"
    else:
        fleche_away = "↑"

    if difference_home < 0:
        fleche_home = "↓"
    else:
        fleche_home = "↑"

    st.markdown(
        f"<h3 style='text-align: center; color: black;'>{round(home_team_cum_prob, 2)} ({home_score})&emsp;&emsp;&emsp;&emsp;&emsp; {round(away_team_cum_prob, 2)} ({away_score})</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<h5 style='text-align: center; color: blue;'>{fleche_home} {difference_home}&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; {fleche_away} {difference_away}</h5>",
        unsafe_allow_html=True,
    )

    st.write(df_shot[features])

    # Charger l'image de la patinoire
    rink_image_path = "figures/nhl_rink.png"  # Remplacez par le chemin réel de votre image
    rink_image = mpimg.imread(rink_image_path)
    
    # Fonction pour visualiser les tirs
    def plot_shots_on_rink(shots_df):
        fig, ax = plt.subplots(figsize=(12, 6))
        # Afficher l'image de la patinoire en arrière-plan
        ax.imshow(rink_image, extent=[-100, 100, -42.5, 42.5], aspect='auto')
        # Tracer les tirs en fonction de leur résultat
        for index, row in shots_df.iterrows():
            if row["event_type"] == "goal":
                color = "green"
                label = "But" if "But" not in ax.get_legend_handles_labels()[1] else None
            
            else:
                color = "blue"
                label = "Raté" if "Raté" not in ax.get_legend_handles_labels()[1] else None
            ax.scatter(
                row["x_coordinate"], row["y_coordinate"], c=color, label=label, alpha=0.7
            )
    
        # Ajouter des légendes
        ax.legend(loc="upper right")
        ax.set_xlim(-100, 100)
        ax.set_ylim(-42.5, 42.5)
        ax.set_title("Visualisation des tirs sur la patinoire")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        return fig
    
    

    # #Tracer les tirs sur la patinoire
    # if not df_shot.empty:             
    #     fig = plot_shots_on_rink(df_shot)            
    #     st.pyplot(fig)        
    # else:             
    #     st.write("Aucun tir enregistré pour ce match.")         # Ajouter un tableau des tirs pour plus de clarté        
    #     st.write("### Détails des tirs") 
    #     st.dataframe(df_shot[["x_coordinate", "y_coordinate", "is_goal", "outcome"]])
    
    # Application Streamlit
    st.title("Visualisation des tirs sur la patinoire")
    st.write("Voici une visualisation des tirs sur la patinoire avec leur résultat : but, arrêt ou raté.")
    
    # Tracer les tirs sur la patinoire
    fig = plot_shots_on_rink(df_shot)
    st.pyplot(fig)
    
    # Ajouter une table des données pour plus de clarté
    st.write("**Données des tirs :**")
    st.dataframe(df_shot)

    import seaborn as sns
 
def plot_heatmap_on_rink(shots_df, rink_image_path):
    """
    Affiche une heatmap des tirs sur la patinoire.
    Args:
        shots_df (DataFrame): Données des tirs avec les colonnes `x_coordinate` et `y_coordinate`.
        rink_image_path (str): Chemin de l'image de la patinoire.
    """
    # Charger l'image de la patinoire
    rink_image = mpimg.imread(rink_image_path)
    # Créer la figure
    fig, ax = plt.subplots(figsize=(12, 6))
    # Afficher l'image de la patinoire
    ax.imshow(rink_image, extent=[-100, 100, -42.5, 42.5], aspect='auto')
    # Ajouter une heatmap des tirs
    sns.kdeplot(
        x=shots_df["x_coordinate"],
        y=shots_df["y_coordinate"],
        fill=True,
        cmap="Reds",
        alpha=0.6,
        levels=100,
        thresh=0.01,
        ax=ax
    )
    # Ajuster les limites de l'axe
    ax.set_xlim(-100, 100)
    ax.set_ylim(-42.5, 42.5)
    ax.set_title("Heatmap des zones de tirs sur la patinoire")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    return fig
 
# Ajouter la section Heatmap dans l'application
if button and not df_shot.empty:
    st.markdown("## Heatmap des zones de tirs")
    rink_image_path = "figures/nhl_rink.png"  # Chemin de l'image de la patinoire
    heatmap_fig = plot_heatmap_on_rink(df_shot, rink_image_path)
    st.pyplot(heatmap_fig)

st.markdown("## Fonctionnalités supplémentaires 🌟")
st.write(
    """
    Nous avons ajouté deux visualisations interactives pour enrichir l'expérience utilisateur :

    1. **Visualisation des tirs** : Chaque tir est affiché dynamiquement sur la patinoire en fonction de ses coordonnées (X, Y). 
       Les tirs sont différenciés par des couleurs selon qu'ils ont été réussis (but), ou ratés. Cela offre une perspective 
       détaillée des performances des joueurs et des gardiens pendant le match.
 

    2. **Heatmap des zones de tirs** : Une carte de chaleur qui identifie les zones les plus ciblées par les tirs 
       sur la patinoire. Cette fonctionnalité utilise une heatmap générée avec `seaborn` pour représenter visuellement 
       les zones chaudes en superposition sur l'image de la patinoire. Elle permet d'analyser les stratégies de tir 
       des équipes en temps réel ou pour des parties passées.

        Ces fonctionnalités ont été conçues pour fournir des insights approfondis aux spectateurs de hockey, rendant 
        l'analyse des matchs plus interactive et visuelle.
    
    """
)
