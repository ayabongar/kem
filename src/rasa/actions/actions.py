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
import re
from actions.constants import (
    RESPONSES,
    RETURN_TO_MENU_BUTTON,
    GOOGLE_MAPS_API_KEY,
    VUMATEL_API_KEY,
    VUMATEL_USER_ID,
    VUMATEL_SESSION_COOKIE
)


environment = os.getenv("ENVIRONMENT")
if environment is not None:
    config_file_path = f"./configs/config.{environment}.json"
else:
    config_file_path = "./configs/config.json"

if not os.path.exists(config_file_path):
    config_file_path = "./configs/config.json"

config = json.loads(open(config_file_path, "r", encoding="utf-8").read())


logger = logging.getLogger(__name__)
setup_logger(logger, config["actionServerLogger"])

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

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Processes location inputs from the user (pin drop or address text).
        """
        user_message = tracker.latest_message.get("text")
        message_payload = tracker.latest_message.get("metadata", {}).get("message", {})

        latitude, longitude = None, None

        if message_payload.get("type") == "LOCATION":
            latitude = message_payload.get("latitude")
            longitude = message_payload.get("longitude")
            if latitude is not None and longitude is not None:
                logger.info(f"Pin location received: {latitude}, {longitude}")
            else:
                logger.error("LOCATION type received, but latitude/longitude is missing.")
                dispatcher.utter_message(json_message=RESPONSES.BuildTextWithButtonsResponse(
                    "Location data is incomplete. Please share a valid location pin.",
                    RETURN_TO_MENU_BUTTON
                ))
                return []

        if latitude is None and longitude is None:
            coordinates = self._get_coordinates_from_input(user_message)
            if coordinates:
                latitude, longitude = coordinates
                logger.info(f"Coordinates extracted from text: {latitude}, {longitude}")
            else:
                coordinates = self._get_coordinates_from_address(user_message, logger)
                if coordinates:
                    latitude, longitude = coordinates
                    logger.info(f"Converted address to coordinates: {latitude}, {longitude}")
                else:
                    dispatcher.utter_message(json_message=RESPONSES.BuildTextWithButtonsResponse(
                        "Couldn't process your location. Please share a valid address or pin.",
                        RETURN_TO_MENU_BUTTON
                    ))
                    return []

        if latitude is not None and longitude is not None:
            dispatcher.utter_message(json_message=RESPONSES.BuildTextResponse(
                "Thank you! I’ve received your location and am checking for outages."
            ))
            return [SlotSet("location_lat", latitude), SlotSet("location_log", longitude)]

        dispatcher.utter_message(json_message=RESPONSES.BuildTextWithButtonsResponse(
            "Unable to process your location. Please try again.",
            RETURN_TO_MENU_BUTTON
        ))
        return []

    def _get_coordinates_from_input(self, user_message: str) -> "tuple[float, float] | None":
        """
        Extracts coordinates from user message text (fallback for text-based coordinates).
        """
        coordinates_match = re.search(r"([-+]?\d{1,5}\.\d+),\s*([-+]?\d{1,5}\.\d+)", user_message)
        if coordinates_match:
            return map(float, coordinates_match.groups())
        return None

    def _get_coordinates_from_address(self, address: str, logger: logging.Logger) -> "tuple[float, float] | None":
        """
        Resolves an address into latitude and longitude using Google Maps API.
        """
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
        logger.info(f"Calling Google Maps API with URL: {geocode_url}")
        try:
            response = requests.get(geocode_url, timeout=10)
            if response.status_code == 200 and response.json()["status"] == "OK":
                location = response.json()["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            logger.error(f"Google Maps API error: {response.text}")
        except requests.RequestException as e:
            logger.error(f"Google Maps API request failed: {str(e)}")
        return None


class ActionCheckOutage(Action):
    def name(self) -> Text:
        return "action_check_outage"
    
    def _check_vumatel_outages(self, latitude: float, longitude: float, logger: logging.Logger) -> str:
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
        print("Running check for outages action")

        latitude = tracker.get_slot("location_lat")
        longitude = tracker.get_slot("location_log")

        message = self._check_vumatel_outages(latitude, longitude, logger)
        logger.debug(f"Message from Vumatel: {message}")
        dispatcher.utter_message(json_message=RESPONSES.BuildTextWithButtonsResponse(message, RETURN_TO_MENU_BUTTON))

        return []
