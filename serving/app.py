"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
import wandb
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import sklearn
import pandas as pd
import joblib
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import json 
import pickle

#import ift6758

app = Flask(__name__)

#import ift6758
LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MB per log file, keep 5 backups
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# Setup model directory
current_script_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_script_path)
parent_dir = os.path.dirname(current_dir)
MODEL_DIR = os.path.join(parent_dir, "models")
if not os.path.exists(MODEL_DIR):
    app.logger.error(f"Model directory does not exist: {MODEL_DIR}")
else:
    app.logger.info(f"Model directory contents: {os.listdir(MODEL_DIR)}")

loaded_model = None


load_dotenv()

# Récupérer la clé API
api_key = os.getenv("API_KEY")

if api_key:
    # Login to Weights & Biases
    wandb.login(key=api_key)
    #logging.info("api key found", api_key)
    logging.info("api key found: "+ api_key[:4] + "****")

else:
    logging.error("API_KEY is not set. WandB functionality will be unavailable.")


# @app.before_first_request
# def before_first_request():
#     """
#     Hook to handle any initialization before the first request (e.g. load model,
#     setup logging handler, etc.)
#     """
#     # TODO: setup basic logging configuration

#logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

#     # TODO: any other initialization before the first request (e.g. load default model)
#     pass

@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    try:
         # Assurez-vous que le fichier existe avant d'essayer de le lire
        if not os.path.exists(LOG_FILE):
            app.logger.error(f"Log file not found at path: {LOG_FILE}")
            return jsonify({"error": f"Log file not found at path: {LOG_FILE}"}), 404

        with open(LOG_FILE, "r") as file:
            response = file.read()
        return jsonify({"logs": response})
    except IOError as e:
        app.logger.error(f"Error reading log file: {e}")
        return jsonify({"error": "Unable to read log file."}), 500
 

@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    
    global loaded_model

    json = request.get_json()
    app.logger.info(json)


    model_name = json["model"]
    entity = json["entity"]
    project = json["project"]
    version = json["version"]
    # Your model loading logic        
    app.logger.info(f"Downloading model: {model_name}, version: {version} from {project} by {entity}")
    #model_path = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")

    #model_path = MODEL_DIR + "/" + model_name + ".pkl"
   #model_path = MODEL_DIR + "/" + model_name + ".joblib"

    if os.path.exists(model_path):
        app.logger.info("Model already downloaded")
       # loaded_model = pickle.load(model_path)  # Load model from joblib file
        with open(model_path, 'rb') as f:
            loaded_model = joblib.load(f)

        return jsonify({"status": "Model already downloaded"})

    try:
        wandb.init(
            project=project,
            entity=entity,
            mode="online"  # ou "offline" si vous voulez éviter les interactions réseau
        )
        app.logger.info(f"Initialisation WandB réussie pour le projet {project} et l'entité {entity}.")

        # Construire le chemin de l'artefact
        artifact_path = f"{entity}/{project}/{model_name}:{version}"
        app.logger.info(f"Downloading model artifact from: {artifact_path}")
        artifact = wandb.use_artifact(artifact_path, type="model")
        artifact_dir = artifact.download(root=MODEL_DIR)

        #model_file_path = os.path.join(artifact_dir, f"{model_name}.joblib")
        model_file_path = os.path.join(artifact_dir, f"{model_name}.pkl")

        loaded_model = joblib.load(model_file_path)
        #loaded_model = pickle.load(model_file_path)

        with open(model_file_path, 'rb') as f:         
            loaded_model = joblib.load(f)     
            app.logger.info("Model downloaded and loaded successfully.")     

        app.logger.info("Model downloaded and loaded successfully.")
        return jsonify({"status": "Model downloaded and loaded successfully."})
    except FileNotFoundError as fnfe:     
        app.logger.error(f"Model file not found: {fnfe}")    
        return jsonify({"error": "Model file not found"}), 404 
    except Exception as e:     
        app.logger.error(f"Failed to download or load model: {e}")     
        return jsonify({"error": f"Server error: {str(e)}"}), 500



@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    
    # if loaded_model is None:
    #     abort(503, description="Model not loaded.")
    if loaded_model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    data = request.get_json()
    app.logger.info(data)
    try:
        app.logger.info(f"Data received: {data}")
        if "columns" in data and "data" in data:
            df = pd.DataFrame(data["data"], columns=data["columns"]).values
            app.logger.info(f"DataFrame created: {df}")
        else:
            app.logger.error("Invalid data format received")
            return jsonify({"error": "Invalid data format"}), 400
        
        prediction = loaded_model.predict_proba(df)[:, 1]
        app.logger.info(f"Prediction completed: {prediction}")
        prediction = prediction.ravel()
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        app.logger.error(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500


import webbrowser
if __name__ == "__main__":
    # Récupération du port à utiliser
    #port = int(os.environ.get("PORT", 8000))
    # Construire l'URL locale
    port = 7000
    url = f"http://0.0.0.0:{port}"
    #url = f"http://127.0.0.1:{port}"

    # Afficher un message dans les logs
    #app.logger.info("Starting server at nnn")
    app.logger.info(f"Starting server at {url}")

    # Ouvrir le lien dans le navigateur par défaut
    #webbrowser.open(url)
    
    # Démarrer l'application Flask
    app.run(host="0.0.0.0", port=port, debug=True)