from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from actions.request_service import RequestService
import logging
import json
import os
from helpers.logging import setup_logger
import requests
import os
import re
from actions.constants import (
    RESPONSES,
    RETURN_TO_MENU_BUTTON,
    YES_NO_BUTTONS,
    GOOGLE_MAPS_API_KEY,
    VUMATEL_API_KEY,
    VUMATEL_USER_ID,
    VUMATEL_SESSION_COOKIE
)

# Load config for environment
environment = os.getenv("ENVIRONMENT")
if environment is not None:
    config_file_path = f"./configs/config.{environment}.json"
else:
    config_file_path = "./configs/config.json"

if not os.path.exists(config_file_path):
    config_file_path = "./configs/config.json"

config = json.loads(open(config_file_path, "r", encoding="utf-8").read())

# Setup Logger
logger = logging.getLogger(__name__)
setup_logger(logger, config["actionServerLogger"])

# Instantiate services
request_service = RequestService(
    logger,
    config["VumatelEndpoint"],
    float(config["request_timeout"]) if "request_timeout" in config.keys() else None,
    float(config["connect_timeout"]) if "connect_timeout" in config.keys() else None
)

class ActionShowMenu(Action):

    def name(self) -> Text:
        return "action_present_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("Running menu action")
        dispatcher.utter_message(json_message=RESPONSES.DEFAULT_MENU)

        return []


class ActionProcessLocation(Action):
    def name(self) -> Text:
        return "action_process_location"

    def _get_coordinates_from_input(self, user_message: str) -> "tuple[str, str] | None":
        coordinates_match = re.search(r"(?P<lat>[-+]?\d{1,3}\.*\d+°? ?S?),\s*(?P<lng>[-+]?\d{1,3}\.*\d+°? ?E?)", user_message)
        if coordinates_match:
            return map(str, coordinates_match.groups())
        return None

    def _get_coordinates_from_address(self, address: str, logger: logging.Logger) -> "tuple[str, str] | None":
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
        logger.info(f"Calling Google Maps API with URL: {geocode_url}")
        response = requests.get(geocode_url)

        if response.status_code == 200 and response.json()["status"] == "OK":
            location = response.json()["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        logger.error(f"Google Maps API response: {response.text}")
        return None

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text')
        
        coordinates = self._get_coordinates_from_input(user_message)
        if coordinates:
            latitude, longitude = coordinates
            logger.info(f"Received coordinates from input: {latitude}, {longitude}")
        else:
            coordinates = self._get_coordinates_from_address(user_message, logger)
            if coordinates:
                latitude, longitude = coordinates
                logger.info(f"Converted address to coordinates: {latitude}, {longitude}")
            else:
                dispatcher.utter_message(json_message = RESPONSES.BuildTextWithButtonsResponse("Couldn't find coordinates for that address.", 
                                                                                                   RETURN_TO_MENU_BUTTON))
                return []

        # Call Vumatel API and send the outage message to the user
        if coordinates:
            #message = self._check_vumatel_outages(latitude, longitude, logger)
            dispatcher.utter_message(json_message = RESPONSES.BuildTextResponse("Thank you! I’ve received your location and are checking for outages."))
            
        return [SlotSet("location_lat", latitude), SlotSet("location_lng", longitude)]




class ActionCheckOutage(Action):
    def name(self) -> Text:
        return "action_check_outage"
    
    def _formatCoordinates(self, latitude: str, longitide: str)-> "tuple[str, str] | None":
        if "° S" in latitude or "° s" in latitude:
            latitude = f"-{latitude[0:-3]}"
        else:
            latitude = latitude[0:-3]
        if "° W" in longitide or "° w" in longitide:
            longitide = f"-{longitide[0:-3]}"
        else:
            longitide = longitide[0:-3]
        return latitude, longitide
    
    def _check_vumatel_outages(self, latitude: str, longitude: str) -> str:
        latitude, longitude = self._formatCoordinates(latitude, longitude)
        vumatel_url = f"{config['VumatelEndpoint']}events/?lat={latitude}&long={longitude}"
        logger.info(f"Calling Vumatel API with URL: {vumatel_url}")

        headers = {
            "APIKEY": VUMATEL_API_KEY,
            "X-USER-ID": VUMATEL_USER_ID,
            "is-internal": "true",
            "Cookie": VUMATEL_SESSION_COOKIE
        }

        try:
            response = requests.get(vumatel_url, headers=headers, timeout=int(config["request_timeout"]))
            if response.status_code == 200:
                events = response.json().get("events", {}).get("results", [])
                if events:
                    return events[0].get("website_description", "No outage details available.")
                return "No outages detected for your location."
            elif response.status_code == 401:
                logger.error("Unauthorized: Check your API key, user ID, or session cookie.")
                return "Failed to check for outages due to unauthorized access. Please contact support."
            else:
                logger.error(f"Vumatel API error: {response.text}")
                return f"Failed to check for outages. Status code: {response.status_code}"
        except Exception as e:
            logger.exception("Error while calling Vumatel API")
            return f"An error occurred while checking outages: {str(e)}"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Leverage ActionProcessLocation logic for location handling
        print("Running check for outages action")

        latitude = tracker.get_slot("location_lat")
        longitude = tracker.get_slot("location_lng")

        message = self._check_vumatel_outages(latitude, longitude)
        logger.debug(f"Message from Vumatel: {message}")
        dispatcher.utter_message(json_message = RESPONSES.BuildTextWithButtonsResponse(f"{message} \n\nIs there anything else you need assistance with?", YES_NO_BUTTONS))

        #await location_action.run(dispatcher, tracker, domain)

        return []
