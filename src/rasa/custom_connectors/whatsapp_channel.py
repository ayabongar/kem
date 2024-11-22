import inspect
import json
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Callable, Awaitable

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)


class WhatsappInputChannel(InputChannel):
    def name(cls) -> Text:
        """Name of your custom channel."""
        return "vumatelwhatsapp"

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender")  # method to get sender_id
            text = request.json.get("text")  # method to fetch text
            input_channel = self.name()  # method to fetch input channel
            metadata = self.get_metadata(request)  # method to get metadata

            collector = CollectingOutputChannel()

            await on_new_message(
                UserMessage(
                    text,
                    collector,
                    sender_id,
                    input_channel=input_channel,
                    metadata=metadata,
                )
            )

            asyncHttp = AsyncHTTPClient()
            try:
                asyncHttp.fetch(
                    HTTPRequest(
                        url="http://localhost:8888/outbound",
                        method="POST",
                        body=json.dumps(collector.messages),
                    ),
                    raise_error=False
                )
                print("Bot response complete")
            except HTTPError as http_err:
                print("HTTPError", http_err)
            except Exception as err:
                print("General Exception", err)

            print("Bot process complete")
            return response.json({})
        return custom_webhook
