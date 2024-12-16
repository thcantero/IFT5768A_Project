import streamlit as st
import pandas as pd
import numpy as np

"""
General template for your streamlit app. 
Feel free to experiment with layout and adding functionality!
Just make sure that the required functionality is included as well
"""

#APP Title
st.title("Expected Goals (xG) Dashboard")

# Sidebar inputs
with st.sidebar:
    with st.sidebar:
    st.header("Model Configuration")
    workspace = st.text_input("Workspace", placeholder="Enter WandB Workspace")
    model_name = st.text_input("Model Name", placeholder="Enter WandB Model Name")
    version = st.text_input("Version", placeholder="Enter Model Version")

    if st.button("Download Model"):
        if workspace and model_name and version:
            # Call the /download_registry_model endpoint
            payload = {"workspace": workspace, "model_name": model_name, "version": version}
            response = requests.post("http://127.0.0.1:8000/download_registry_model", json=payload)
            if response.status_code == 200:
                st.success("Model downloaded and loaded successfully!")
            else:
                st.error(f"Error: {response.json().get('description', 'Unknown error')}")
        else:
            st.error("Please fill in all fields for workspace, model name, and version.")
    pass

# Game ID input
with st.container():
    st.header("Game Analysis")
    game_id = st.text_input("Game ID", placeholder="Enter NHL Game ID")

    if st.button("Analyze Game"):
        if game_id:
            # Fetch game data from GameClient
            try:
                response = requests.get(f"http://127.0.0.1:8000/game/{game_id}")
                if response.status_code == 200:
                    game_data = response.json()
                    
                    # Extract relevant game info
                    home_team = game_data.get("home_team", "Unknown")
                    away_team = game_data.get("away_team", "Unknown")
                    period = game_data.get("period", "Unknown")
                    time_remaining = game_data.get("time_remaining", "Unknown")
                    home_score = game_data.get("home_score", 0)
                    away_score = game_data.get("away_score", 0)
                    home_xg = game_data.get("home_xg", 0.0)
                    away_xg = game_data.get("away_xg", 0.0)

                    # Display game info
                    st.write(f"**Home Team:** {home_team} ({home_score} goals)")
                    st.write(f"**Away Team:** {away_team} ({away_score} goals)")
                    st.write(f"**Current Period:** {period}")
                    st.write(f"**Time Remaining:** {time_remaining}")
                    st.write(f"**Expected Goals (xG):**")
                    st.write(f"- **Home Team (xG):** {home_xg}")
                    st.write(f"- **Away Team (xG):** {away_xg}")

                    # Calculate xG difference
                    st.write(f"**xG Difference (Home):** {home_xg - home_score:.2f}")
                    st.write(f"**xG Difference (Away):** {away_xg - away_score:.2f}")
                else:
                    st.error("Error fetching game data. Please check the Game ID.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a valid Game ID.")
    pass

with st.container():
    # TODO: Add Game info and predictions
    st.subheader("Game Info and Predictions")
    st.write(f"**Home Team:** {home_team} ({home_score} goals)")
    st.write(f"**Away Team:** {away_team} ({away_score} goals)")
    st.write(f"**Current Period:** {period}")
    st.write(f"**Time Remaining:** {time_remaining}")
    st.write(f"**Expected Goals (xG):**")
    st.write(f"- **Home Team (xG):** {home_xg}")
    st.write(f"- **Away Team (xG):** {away_xg}")

    home_diff = home_xg - home_score
    away_diff = away_xg - away_score
    st.write(f"**xG Difference (Home):** {home_diff:.2f}")
    st.write(f"**xG Difference (Away):** {away_diff:.2f}")
    pass

with st.container():
    # TODO: Add data used for predictions
    st.subheader("Data Used for Predictions")
    prediction_response = requests.get(f"http://127.0.0.1:8000/predictions/{game_id}")
    if prediction_response.status_code == 200:
        prediction_data = prediction_response.json()
        df = pd.DataFrame(prediction_data)
        st.dataframe(df)
    else:
        st.error("Error fetching prediction data.")
    pass