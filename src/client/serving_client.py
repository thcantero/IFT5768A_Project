import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 7000, features=None):
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

        url = f"{self.base_url}/predict"
        payload = X.to_json(orient="split")
        headers = {"Content-Type": "application/json"}
        try:
            #response = requests.get(url, data=payload, headers=headers)
            logger.debug(f"Payload sent to the server: {payload}")
            logger.debug(f"Sending request to URL: {url}")
            response = requests.post(url, data=payload, headers=headers)

            response.raise_for_status()
            try:
                response_json = response.json()
            except ValueError as ve:
                logger.error(f"Invalid JSON response: {response.text}")
                raise ValueError("The server did not return a valid JSON response.") from ve

            predictions = pd.DataFrame(response_json)
            predictions.index = X.index  # Align index if necessary
            return predictions
        
        except Exception as e:
            logger.error(f"Exception during predict: {e}")
            raise
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            logger.error(f"Response content: {response.text}")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error occurred: {conn_err}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
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

    def download_registry_model(self, entity:str, project: str, model: str, version: str) -> dict:
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
                #payload = json.dumps({"entity":entity, "project": project, "model": model, "version": version})
                payload = {"entity":entity, "project": project, "model": model, "version": version}

                headers = {"Content-Type": "application/json"}
                
                logger.debug(f"Payload sent to the server: {payload}")
                logger.debug(f"Sending request to URL: {url}")
                
                response = requests.post(url, json=payload, headers=headers)
                #response = requests.get(url, json=payload, headers=headers)

                if response.status_code != 200:
                    logger.error(f"Error downloading model: {response.status_code}, {response.text}")
                    response.raise_for_status()
                logger.info(response)

                return response.json()

            except Exception as e:
                logger.error(f"Exception during model download: {e}")
                raise

        #raise NotImplementedError("TODO: implement this function")

# import json
# import requests
# import pandas as pd
# import logging


# logger = logging.getLogger(__name__)


# class ServingClient:
#     def __init__(self, ip: str = "0.0.0.0", port: int = 5000, features=None):
#         self.base_url = f"http://{ip}:{port}"
#         logger.info(f"Initializing client; base URL: {self.base_url}")

#         if features is None:
#             features = ["distance"]
#         self.features = features

#         # any other potential initialization

#     def predict(self, X: pd.DataFrame) -> pd.DataFrame:
#         """
#         Formats the inputs into an appropriate payload for a POST request, and queries the
#         prediction service. Retrieves the response from the server, and processes it back into a
#         dataframe that corresponds index-wise to the input dataframe.
        
#         Args:
#             X (Dataframe): Input dataframe to submit to the prediction service.
#         """

#         try:
#             url = f"{self.base_url}/predict"
#             payload = X.to_json(orient="records")
#             headers = {"Content-Type": "application/json"}
#             response = requests.post(url, data=payload, headers=headers)

#             if response.status_code != 200:
#                 logger.error(f"Error in prediction: {response.status_code}, {response.text}")
#                 response.raise_for_status()

#             predictions = response.json().get("predictions", [])
#             return pd.DataFrame(predictions, columns=["predictions"], index=X.index)

#         except Exception as e:
#             logger.error(f"Exception during predict: {e}")
#             raise
        
#         #raise NotImplementedError("TODO: implement this function")

#     def logs(self) -> dict:
#         """Get server logs"""
#         try:
#             url = f"{self.base_url}/logs"
#             response = requests.get(url)

#             if response.status_code != 200:
#                 logger.error(f"Error retrieving logs: {response.status_code}, {response.text}")
#                 response.raise_for_status()

#             return response.json().get("logs", {})

#         except Exception as e:
#             logger.error(f"Exception during logs retrieval: {e}")
#             raise

#         #raise NotImplementedError("TODO: implement this function")

# def download_registry_model(self, entity:str, project: str, model: str, version: str) -> dict:
#         """
#         Triggers a "model swap" in the service; the workspace, model, and model version are
#         specified and the service looks for this model in the model registry and tries to
#         download it. 

#         See more here:

#             https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
#         Args:
#             workspace (str): The Comet ML workspace
#             model (str): The model in the Comet ML registry to download
#             version (str): The model version to download
#         """
#         try:
#             url = f"{self.base_url}/download_registry_model"
#             payload = json.dumps({"entity":entity, "project": project, "model": model, "version": version})
#             headers = {"Content-Type": "application/json"}
#             response = requests.post(url, json=payload, headers=headers)

#             if response.status_code != 200:
#                 logger.error(f"Error downloading model: {response.status_code}, {response.text}")
#                 response.raise_for_status()

#             return response.json()

#         except Exception as e:
#             logger.error(f"Exception during model download: {e}")
#             raise

#         #raise NotImplementedError("TODO: implement this function")
