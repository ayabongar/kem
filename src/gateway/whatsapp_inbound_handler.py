from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
import json
import tornado.web
from torndsession.sessionhandler import SessionBaseHandler


class WhatsappInboundHandler(SessionBaseHandler):
    async def post(self):
        print("received whatsapp message")
        whatsapp_message = json.loads(self.request.body)
        whatsapp_result = whatsapp_message["results"][0]
        print("Message Received from WhatsApp: ", whatsapp_result)

        self.session["sender"] = whatsapp_result["from"]


        data = {
            "sender": whatsapp_result["from"],
            "text": "",
            "metadata": {}
        }

        message_type = whatsapp_result["message"]["type"]

        try:
            if message_type == "TEXT":
                data["text"] = whatsapp_result["message"]["text"]

            elif message_type == "INTERACTIVE_LIST_REPLY":
                data["text"] = whatsapp_result["message"]["id"]

            elif message_type == "INTERACTIVE_BUTTON_REPLY":
                data["text"] = whatsapp_result["message"]["id"]

            elif message_type == "LOCATION":
                latitude = whatsapp_result["message"].get("latitude")
                longitude = whatsapp_result["message"].get("longitude")
                if latitude is not None and longitude is not None:
                    data["text"] = f"{latitude},{longitude}"
                else:
                    raise KeyError("Missing latitude or longitude in LOCATION message")

            else:          
                print(f"Unsupported message type received: {message_type}")
                self.set_status(400)
                self.finish()
                return

            async_http = AsyncHTTPClient()
            response = await async_http.fetch(
                HTTPRequest(
                    "http://localhost:5002/webhooks/vumatelwhatsapp/webhook",
                    method="POST",
                    body=json.dumps(data),
                    headers={"Content-Type": "application/json"}
                ),
                raise_error=False
            )
            print(f"Message forwarded to bot. Response status: {response.code}")

        except KeyError as e:
            print(f"KeyError: {str(e)}")
            self.set_status(400)  
        except HTTPError as http_err:
            print(f"HTTPError while forwarding message: {http_err}")
            self.set_status(http_err.code)
        except Exception as err:
            print(f"General Exception while forwarding message: {err}")
            self.set_status(500) 

        self.finish()
