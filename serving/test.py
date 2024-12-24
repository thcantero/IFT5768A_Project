
from flask import jsonify
import requests

# URL du point de terminaison Flask
#url = "http://localhost:5001/download_registry_model"

url = "http://localhost:7000/download_registry_model"

# Payload JSON avec les données nécessaires
#expected-goal-distance:v1
#expected-goal-model-angle-and-distance:v1
payload = {
    "entity":"thalia-cantero-udem",
    "project":"IFT6758.2024-A04",
    "model": "expected-goal-model-angle-and-distance",
    "version": "v1"
    }
#runs/
# Envoi de la requête POST
response = requests.post(url, json=payload)

# Affichage de la réponse
print(response.status_code)  # Devrait être 200 si tout est correct
print(response.json())       # Réponse JSON renvoyée par Flask



import requests
import json
import pandas as pd

# URL de l'API Flask
url = "http://localhost:7000/predict"
#url = "http://localhost:5001/predict"


# Charger les données
data_path = "C:/Users/Cloud/OneDrive/Bureau/UdeM/Session d'automne/data Science/projet3/python/milestone3/docker-project (1)/docker-project/data/Q4_train.csv"
data = pd.read_csv(data_path)

# Sélectionner uniquement les colonnes nécessaires (features utilisées par le modèle)
features = ["distance", "angle"]  # Ajustez selon les colonnes utilisées par votre modèle
df_features = data[features]

# Convertir le DataFrame en JSON
payload = df_features.to_json(orient="split")

# Envoyer la requête POST
try:
    response = requests.post(url, json=json.loads(payload))  # Utiliser POST avec payload JSON

    # Vérification de la réponse
    if response.status_code == 200:
        print("Prédictions :")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Erreur : {response.status_code}")
        print(response.text)  # Afficher les détails de l'erreur
except Exception as e:
    print(f"Erreur lors de la requête : {e}")
