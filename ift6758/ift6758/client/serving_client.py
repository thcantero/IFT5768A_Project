import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 8000, features=None):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["distance"]
        self.features = features

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """

        try:
            url = f"{self.base_url}/predict"
            payload = X.to_json(orient="records")
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, data=payload, headers=headers)

            if response.status_code != 200:
                logger.error(f"Error in prediction: {response.status_code}, {response.text}")
                response.raise_for_status()

            predictions = response.json().get("predictions", [])
            return pd.DataFrame(predictions, columns=["predictions"], index=X.index)

        except Exception as e:
            logger.error(f"Exception during predict: {e}")
            raise
        
        #raise NotImplementedError("TODO: implement this function")

    def logs(self) -> dict:
        """Get server logs"""
        try:
            url = f"{self.base_url}/logs"
            response = requests.get(url)

            if response.status_code != 200:
                logger.error(f"Error retrieving logs: {response.status_code}, {response.text}")
                response.raise_for_status()

            return response.json().get("logs", {})

        except Exception as e:
            logger.error(f"Exception during logs retrieval: {e}")
            raise

        #raise NotImplementedError("TODO: implement this function")

    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """
        try:
            url = f"{self.base_url}/download_registry_model"
            payload = {
                "workspace": workspace,
                "model_name": model,
                "version": version
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                logger.error(f"Error downloading model: {response.status_code}, {response.text}")
                response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Exception during model download: {e}")
            raise

        #raise NotImplementedError("TODO: implement this function")
