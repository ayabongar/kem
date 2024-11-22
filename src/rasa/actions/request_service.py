from typing import Text, Dict, Any, Union
from logging import Logger
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPResponse, HTTPError

import json
import time

from actions.constants import (
    OUTAGE_EVENT,
    SERVICE_UNAVAILABLE
)

class RequestService:
    def __init__(
        self,
        logger: Logger,
        vumatel_endpoint: Text,
        request_timeout: Union[float, None],
        connect_timeout: Union[float, None],
    ):
        """
        Sends the various http requests that the action server supports

        :arg Logger logger: A logger object
        :arg Text vumatel_endpoint: The base endpoint for the ATP service, used for all service requests to ATP
        :arg Text request_timeout: The timeout for the entire http request in seconds, if left blank then the default tornado http client timeout is used
        :arg Text connect_timeout: The timeout for the initial connection of a request, if left blank the default tornado http client timeout is used
        """

        self.vumatel_endpoint = vumatel_endpoint
        self.logger = logger
        self.request_timeout = request_timeout  # request_timeout
        self.connect_timeout = connect_timeout

    async def get_request(
        self, endpoint: Text, tail: Text, session_id: Text, querystring: Text = ""
    ) -> Dict[Text, Any]:
        asyncHttp = AsyncHTTPClient()
        try:
            url = endpoint + tail
            headers = {
                "Content-type": "application/json",
                "Cookie": "sessionid=t9y5y8de86qveqxfifjh3lwsb0je3aiv",
                "X-USER-ID": "84",
                "is-interna": "true",
                "APIKEY": "5Cx0pfnMlp6IDoGmiLS4MLIhtHnWJtk1"
                }
            self.logger.info(f"[{session_id}] - Sending GET request to url - {url}")
            start = time.time()
            response: HTTPResponse = await asyncHttp.fetch(
                HTTPRequest(
                    url + querystring,
                    headers=headers,
                    method="GET",
                    request_timeout=self.request_timeout,
                    connect_timeout=self.connect_timeout,
                )
            )
            end = time.time()
            self.logger.info(
                f"[{session_id}] - Received response from {url} (took {round((end - start) * 1000, 2)} milliseconds) with code {response.code} - {response.body}"
            )
            json_response = json.loads(response.body)
            return json_response
        except HTTPError as http_err:
            self.logger.error(f"[{session_id}] - HTTP error occurred: {str(http_err)}")
            raise Exception(SERVICE_UNAVAILABLE)
        except Exception as err:
            self.logger.error(f"[{session_id}] - General error occurred: {str(err)}")
            raise Exception(SERVICE_UNAVAILABLE)

    async def post_request(
        self, body: Dict[Text, Any], endpoint: Text, tail: Text, session_id: Text
    ) -> Dict[Text, Any]:
        asyncHttp = AsyncHTTPClient()
        try:
            url = endpoint + tail
            headers = {"Content-type": "application/json"}
            self.logger.info(f"[{session_id}] - Sending POST request to url - {url}, with data - {body}")
            start = time.time()
            response: HTTPResponse = await asyncHttp.fetch(
                HTTPRequest(
                    url,
                    body=json.dumps(body),
                    headers=headers,
                    method="POST",
                    request_timeout=self.request_timeout,
                    connect_timeout=self.connect_timeout,
                )
            )
            end = time.time()
            self.logger.info(
                f"[{session_id}] - Received response from {url} (took {round((end - start) * 1000, 2)} milliseconds) with code {response.code} - {response.body}"
            )
            json_response = json.loads(response.body)
            return json_response
        except HTTPError as http_err:
            self.logger.error(f"[{session_id}] - HTTP error occurred: {str(http_err)}")
            raise Exception(SERVICE_UNAVAILABLE)
        except Exception as err:
            self.logger.error(f"[{session_id}] - General error occurred: {str(err)}")
            raise Exception(SERVICE_UNAVAILABLE)

    async def put_request(self, body: Dict[Text, Any], endpoint: Text, tail: Text, session_id: Text) -> Dict[Text, Any]:
        asyncHttp = AsyncHTTPClient()
        try:
            url = endpoint + tail
            headers = {"Content-type": "application/json"}
            self.logger.info(f"[{session_id}] - Sending PUT request to url - {url}, with data - {body}")
            start = time.time()
            response: HTTPResponse = await asyncHttp.fetch(
                HTTPRequest(
                    url,
                    body=json.dumps(body),
                    headers=headers,
                    method="PUT",
                    request_timeout=self.request_timeout,
                    connect_timeout=self.connect_timeout,
                )
            )
            end = time.time()
            self.logger.info(
                f"[{session_id}] - Received response from {url} (took {round((end - start) * 1000, 2)} milliseconds) with code {response.code} - {response.body}"
            )
            json_response = json.loads(response.body)
            return json_response
        except HTTPError as http_err:
            self.logger.error(f"[{session_id}] - HTTP error occurred: {str(http_err)}")
            raise Exception(SERVICE_UNAVAILABLE)
        except Exception as err:
            self.logger.error(f"[{session_id}] - General error occurred: {str(err)}")
            raise Exception(SERVICE_UNAVAILABLE)

    async def action_get_outage_event(self, session_id: Text, location_reference: Text) -> Dict[Text, Any]:
        return await self.get_request(self.vumatel_endpoint, OUTAGE_EVENT, session_id, f"?location_reference={location_reference}")
