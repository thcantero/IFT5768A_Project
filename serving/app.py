import os
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import sklearn
import pandas as pd
import joblib
import numpy as np

# from ift6758.client import CometMLClient


app = Flask(__name__)


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
MODEL_DIR = os.environ.get("MODEL_DIR", "./comet_models")


# global model so you don't need to reload it on every predict request
model = None
comet_client = None


def load_model(path: str = "model/logreg.joblib") -> sklearn.base.BaseEstimator:
    """
    Loads a model from the specified path using joblib pickling, assigns it
    to the global model variable

    Args:
        path (str): path to the model.pkl file to load
    """
    # to modify a global variable, first call the global keyword
    global model
    new_model = joblib.load(path)

    if new_model is None:
        app.logger.info(f"Model failed to load from: {path}")
        return

    model = new_model
    app.logger.info(f"Model loaded from: {path}")


def load_comet():
    api_key = os.environ.get("COMET_API_KEY", None)
    if api_key is None:
        app.logger.warning("Comet ML API key is not set - Comet functionality is disabled")
        return

    global comet_client
    comet_client = CometMLClient(api_key, MODEL_DIR)


@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    # Setup logger
    format = "%(asctime)s;%(levelname)s;%(message)s"
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=format)
    app.logger.info("Before first request")

    # # Load baseline model
    # load_model()

    # # Setup Comet API
    # load_comet()


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    Expects json with the schema:

    {
        workspace: (required),
        model: (required),
        version: (required),
        overwrite: (optional, default=False),
        extension: (optional, default='.joblib')
    }

    Updates model
    """
    if comet_client is None:
        message = "Comet ML API key is not set - Comet functionality is disabled"
        app.logger.warning(message)
        abort(400, message)

    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    new_model = comet_client.download_registry_model(**json)
    load_model(new_model)

    message = f"New model loaded from: '{new_model}'"
    app.logger.info(message)
    return jsonify(message)


@app.route("/logs", methods=["GET"])
def get_logs():
    with open(LOG_FILE) as f:
        data = f.read().splitlines()
    return jsonify(data)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    # Convert to dataframe
    df = pd.DataFrame(json)

    # # init the model if it hasn't been loaded yet
    # if model is None:
    #     load_model()

    # # make predictions
    # y = model.predict_proba(df)

    # # return response
    y = np.array([[10, 20], [30, 20]])
    result = pd.DataFrame({"shot_pred": y[:, 0], "goal_pred": y[:, 1]})
    app.logger.info(result)
    return jsonify(result.to_json())
