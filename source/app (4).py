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


#import ift6758
app = Flask(__name__)



LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
DEFAULT_MODEL_PATH = "default_model.pkl"  # Placeholder for the default model
WANDB_API_KEY = os.getenv("WANDB_API_KEY")

if WANDB_API_KEY:
    # Login to Weights & Biases
    wandb.login(key=WANDB_API_KEY)
else:
    logging.error("WANDB_API_KEY is not set. WandB functionality will be unavailable.")

# Global model variable
current_model = None




@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    # TODO: setup basic logging configuration
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO,  format="%(asctime)s - %(message)s")
    
    # TODO: any other initialization before the first request (e.g. load default model)
        # Create the log file if it does not exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.write("")  # Create an empty log file

    # Load default model
    global current_model
    if os.path.exists(DEFAULT_MODEL_PATH):
        current_model = joblib.load(DEFAULT_MODEL_PATH)
        logging.info("Loaded default model from %s", DEFAULT_MODEL_PATH)
    else:
        logging.warning("Default model not found, application started without a model")

@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    # TODO: read the log file specified and return the data
    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "Log file not found"}), 404
    #raise NotImplementedError("TODO: implement this endpoint")
    with open(LOG_FILE, 'r') as log_file:
        log_data = log_file.readlines()
    return jsonify({"logs": log_data})
    #response = None
    #return jsonify(response)  # response must be json serializable!


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
    # Get POST json data
    data = request.get_json()
    app.logger.info(data)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    workspace = data.get("workspace")
    model_name = data.get("model")
    version = data.get("version")

    if not all([workspace, model_name, version]):
        return jsonify({"error": "Missing required fields: workspace, model, version"}), 400
    
    # TODO: check to see if the model you are querying for is already downloaded

    # TODO: if yes, load that model and write to the log about the model change.  
    # eg: app.logger.info(<LOG STRING>)
    
    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model

    # Tip: you can implement a "CometMLClient" similar to your App client to abstract all of this
    # logic and querying of the CometML servers away to keep it clean here
    model_path = f"{model_name}_v{version}.pkl"  # Example model path
    global current_model
    try:

        if os.path.exists(model_path):
            # Model already downloaded
            current_model = joblib.load(model_path)
            logging.info("Loaded model %s version %s from local storage", model_name, version)
        else:
            # Simulate downloading the model
            logging.info(f"Attempting to download model {model_name} version {version} from WandB.")
            # Code to download model (e.g., using Comet/Wandb API) would go here
            api = wandb.Api()
            artifact_name = f"{workspace}/{model_name}:v{version}"
            artifact = api.artifact(artifact_name)
            artifact_dir = artifact.download()
            downloaded_model_path = os.path.join(artifact_dir, model_path)
            os.rename(downloaded_model_path, model_path)
            current_model = joblib.load(model_path)
            logging.info(f"Successfully downloaded and loaded model {model_name} version {version}.")

            # For demonstration, create a dummy model file
    except wandb.errors.CommError as e:
        logging.error(f"Failed to connect to WandB: {e}")
        return jsonify({"error": "Failed to connect to WandB."}), 500
    except FileNotFoundError as e:
        logging.error(f"Model artifact not found: {e}")
        return jsonify({"error": "Model artifact not found."}), 404
    except Exception as e:
        logging.error(f"Unexpected error while loading model: {e}")
        return jsonify({"error": "Unexpected error occurred."}), 500
    

    return jsonify({"message": "Model loaded successfully", "model": model_name, "version": version})

    #raise NotImplementedError("TODO: implement this endpoint")
    #response = None
    #app.logger.info(response)
    #return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    global current_model
    if current_model is None:
        return jsonify({"error": "No model is currently loaded"}), 400
    
    # Get POST json data
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    app.logger.info(data)

    # TODO:
    #raise NotImplementedError("TODO: implement this enpdoint")
    
    #response = None

    #app.logger.info(response)
    #return jsonify(response)  # response must be json serializable!

    try:
        # Convert JSON input to DataFrame
        features_df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)

        # Make predictions
        predictions = current_model.predict(features_df)
        logging.info("Predictions made successfully: %s", predictions.tolist())
        return jsonify({"predictions": predictions.tolist()})
    except Exception as e:
        logging.error("Prediction failed: %s", str(e))
        return jsonify({"error": "Prediction failed"}), 500

if __name__ == "__main__":
    # Start the Flask application
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)