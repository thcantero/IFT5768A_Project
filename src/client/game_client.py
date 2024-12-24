import requests

from src.features.clean import clean_row


class GameClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 7000):
        self.base_url = f"http://{ip}:{port}"

        self.processed = {}

    def fetch_live_game_data(self, game_id):
        url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"

        try:
            response = requests.get(url)
        except:
            game_data = "vide"

        if response.status_code == 200:
            game_data = (
                response.json()
            )  # This will be a JSON object containing game data
        else:
            game_data = "vide"

        return game_data

    def make_prediction(self, features):
        url = f"{self.base_url}/predict"
        response = requests.post(url, json=features)
        return response.json()

    def process_events(self, events):
        for event in events:
            if event["gameID"] not in self.processed.keys():
                features = clean_row(event)
                preds = self.make_prediction(features)
                self.processed[event["gameID"]] = preds


# import requests
# import pandas as pd
# import logging


# logger = logging.getLogger(__name__)


# class GameClient:
#     def __init__(self, game_id: str, base_url: str = "https://api-web.nhle.com/v1/gamecenter", prediction_service_url: str = "http://0.0.0.0:5000"):
#         self.game_id = game_id
#         self.base_url = base_url
#         self.prediction_service_url = prediction_service_url
#         self.processed_events = set()  # To track processed event IDs
#         logger.info(f"GameClient initialized for game ID: {game_id}")

#     def fetch_live_game_data(self) -> dict:
#         '''Fetches live game data from the NHL API for the specified game ID.'''
        
#         try:
#             url = f"{self.base_url}/{self.game_id}/play-by-play"
#             response = requests.get(url)

#             if response.status_code != 200:
#                 logger.error(f"Error fetching live game data: {response.status_code}, {response.text}")
#                 response.raise_for_status()

#             return response.json()
#         except Exception as e:
#             logger.error(f"Exception fetching live game data: {e}")
#             raise

#     def process_new_events(self, game_data: dict):
#         '''Processes new events from the live game data, computes features, and sends predictions.'''
#         try:
#             plays = game_data.get("plays", {}).get("allPlays", [])
#             new_events = [play for play in plays if play.get("about", {}).get("eventId") not in self.processed_events]

#             for event in new_events:
#                 event_id = event.get("about", {}).get("eventId")
#                 features = self.extract_features(event)
#                 prediction = self.send_prediction_request(features)

#                 logger.info(f"Event ID: {event_id}, Prediction: {prediction}")
#                 self.processed_events.add(event_id)
#         except Exception as e:
#             logger.error(f"Exception processing new events: {e}")
#             raise

#     def extract_features(self, event: dict) -> pd.DataFrame:
#         '''Extracts features required by the prediction model from a single event.'''
        
#         try:
#             # Example feature extraction logic
#             distance = event.get("coordinates", {}).get("x", 0)
#             angle = event.get("coordinates", {}).get("y", 0)
#             features = pd.DataFrame([{"distance": distance, "angle": angle}])

#             return features
#         except Exception as e:
#             logger.error(f"Exception extracting features: {e}")
#             raise

#     def send_prediction_request(self, features: pd.DataFrame) -> dict:
#         '''Sends the extracted features to the prediction service and retrieves predictions.'''
        
#         try:
#             url = f"{self.prediction_service_url}/predict"
#             payload = features.to_json(orient="records")
#             headers = {"Content-Type": "application/json"}
#             response = requests.post(url, data=payload, headers=headers)

#             if response.status_code != 200:
#                 logger.error(f"Error in prediction request: {response.status_code}, {response.text}")
#                 response.raise_for_status()

#             return response.json()
#         except Exception as e:
#             logger.error(f"Exception during prediction request: {e}")
#             raise

#     def update_tracker(self, last_event_id: int):
#         # Updates the tracker with the last processed event ID.
#         self.processed_events.add(last_event_id)


# if __name__ == "__main__":
#     # Example usage
#     game_id = "2022030411"  # Replace with actual game ID
#     client = GameClient(game_id)

#     try:
#         game_data = client.fetch_live_game_data()
#         client.process_new_events(game_data)
#     except Exception as e:
#         logger.error(f"Error in GameClient: {e}")
