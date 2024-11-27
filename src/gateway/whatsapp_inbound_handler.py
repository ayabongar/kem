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
        if whatsapp_result["message"]["type"] == "TEXT":
            data = {
                "sender": whatsapp_result["from"],
                "text": whatsapp_result["message"]["text"],
                "metadata": {}
            }
        elif whatsapp_result["message"]["type"] == "INTERACTIVE_LIST_REPLY":
            data = {
                "sender": whatsapp_result["from"],
                "text": whatsapp_result["message"]["id"],
                "metadata": {}
            }
        elif whatsapp_result["message"]["type"] == "INTERACTIVE_BUTTON_REPLY":
            data = {
                "sender": whatsapp_result["from"],
                "text": whatsapp_result["message"]["id"],
                "metadata":{}
            }
        elif whatsapp_result["message"]["type"] == "LOCATION":
            text = f"{whatsapp_result['message']['latitude']}, {whatsapp_result['message']['longitude']}"
            data = {
                "sender": whatsapp_result["from"],
                "text": text,
                "metadata":{}
            }

        asyncHttp = AsyncHTTPClient()
        try:
            asyncHttp.fetch(
                HTTPRequest(
                    "http://localhost:5002/webhooks/vumatelwhatsapp/webhook",
                    method="POST",
                    body=json.dumps(data),
                ),
                raise_error=False
            )
        except HTTPError as http_err:
            print("HTTPError", http_err)
        except Exception as err:
            print("General Exception", err)

        print("Message forwarded to bot.")

        self.set_status(200)
        self.finish()