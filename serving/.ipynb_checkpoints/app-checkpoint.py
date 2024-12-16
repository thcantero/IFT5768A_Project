import os
import wandb
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import pandas as pd
import joblib

app = Flask(__name__)

LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
DEFAULT_MODEL_PATH = "default_model.pkl"
WANDB_API_KEY = os.getenv("WANDB_API_KEY")

if WANDB_API_KEY:
    wandb.login(key=WANDB_API_KEY)
else:
    logging.error("WANDB_API_KEY is not set. WandB functionality will be unavailable.")

# Global model variable
current_model = None

@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request
    """
    # Basic logging configuration (file only)
    file_handler = logging.FileHandler(LOG_FILE)
    console_handler = logging.StreamHandler()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[file_handler, console_handler])


    # Log initialization message
    logging.info("Logging initialized.")

@app.route("/", methods=["GET"])
def index():
    """Default route to check the health of the application."""
    return jsonify(
        message="Flask application is running",
        endpoints=["/predict (POST)", "/logs (GET)", "/download_registry_model (POST)"]
    )

@app.route("/logs", methods=["GET"])
def logs():
    try:
        with open(LOG_FILE, "r") as log_file:
            log_content = log_file.read()
        return jsonify(logs=log_content.splitlines())
    except Exception as e:
        abort(500, description=f"Error reading log file: {e}")

@app.route("/predict", methods=["POST"])
def predict():
    global current_model
    if current_model is None:
        abort(500, description="No model loaded. Please load a model using /download_registry_model.")

    try:
        input_data = request.json
        if not input_data:
            abort(400, description="Input data is missing.")
        
        df = pd.DataFrame(input_data)
        predictions = current_model.predict_proba(df)[:, 1]
        return jsonify(predictions=predictions.tolist())
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        abort(500, description=f"Prediction error: {e}")

@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    global current_model
    request_data = request.json
    workspace = request_data.get("workspace")
    model_name = request_data.get("model_name")
    version = request_data.get("version")

    if not all([workspace, model_name, version]):
        abort(400, description="Missing workspace, model_name, or version.")

    try:
        artifact_path = f"{workspace}/{model_name}:{version}"
        artifact = wandb.Api().artifact(artifact_path)
        model_path = artifact.download()
        model_file = os.path.join(model_path, "model.pkl")

        if os.path.exists(model_file):
            current_model = joblib.load(model_file)
            logging.info(f"Model loaded: {artifact_path}")
            return jsonify(message="Model downloaded and loaded successfully.")
        else:
            logging.error(f"Model file not found in artifact: {artifact_path}")
            abort(500, description="Model file not found in artifact.")
    except Exception as e:
        logging.error(f"Error downloading model: {e}")
        abort(500, description=f"Error downloading model: {e}")
        
@app.route("/game/<game_id>", methods=["GET"])
def get_game_data(game_id):
    # Fetch game data using GameClient
    client = GameClient(game_id)
    try:
        game_data = client.fetch_live_game_data()
        return jsonify(game_data)
    except Exception as e:
        logging.error(f"Error fetching game data for {game_id}: {e}")
        abort(500, description=f"Error fetching game data: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
