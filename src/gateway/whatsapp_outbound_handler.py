import tornado.web
import json
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from torndsession.sessionhandler import SessionBaseHandler

base_url = ""
api_key = ""


class WhatsappOutboundHandler(SessionBaseHandler):
    async def post(self):
        print("starting outbound process...")
        bot_responses = json.loads(self.request.body)
        print(f"response from rasa: {bot_responses}")

        if 'sender' in self.session:
            session_id = self.session['sender']
            print(f"sender: {session_id}")
        
        for bot_response in bot_responses:
            if bot_response.get("text") is not None:
                data, template_url = self.BuildTextResponse(bot_response, bot_response["recipient_id"])
            elif bot_response["custom"].get("type") == "INTERACTIVE_LIST":
                data, template_url = self.BuildInteractiveList(bot_response["custom"], bot_response["recipient_id"])
            elif bot_response["custom"].get("type") == "TEXT":
                data, template_url = self.BuildTextResponse(bot_response["custom"], bot_response["recipient_id"])

            print(f"Data for Infobip: {data}")

            asyncHttp = AsyncHTTPClient()
            asyncHttp.fetch(
                HTTPRequest(
                    base_url + template_url,
                    headers={"Authorization": f"App {api_key}", "Content-Type": "application/json"},
                    method="POST",
                    body=json.dumps(data),
                ),
                raise_error=False
            )
        print("outbound process complete")

        self.set_status(200)
        self.finish()
    
    def BuildTextResponse(self, bot_response, recipient_id):
        if "buttons" in bot_response and bot_response["buttons"] != "":
            payload = {
                    "from": "447860099299",
                    "to": recipient_id,
                    "messageId": "a28dd97c-1ffb-4fcf-99f1-0b557ed381da",
                    "content": {
                        "body": {
                            "text": bot_response["text"]
                        },
                        "action": {
                            "buttons": self.BuildInteractiveButtons(bot_response["buttons"])
                        }
                    }
                }
            template_url = "/whatsapp/1/message/interactive/buttons"
        else:
            payload = {
                    "from": "447860099299",
                    "to": recipient_id,
                    "messageId": "a28dd97c-1ffb-4fcf-99f1-0b557ed381da",
                    "content": {
                        "text": bot_response["text"]
                    }
                }
            template_url = "/whatsapp/1/message/text"

        return payload, template_url
    
    def BuildInteractiveList(self, bot_response, recipient_id):
        payload = {
            "from": "447860099299",
            "to": recipient_id,
            "messageId": "a28dd97c-1ffb-4fcf-99f1-0b557ed381da",
            "content": {
                "body": {
                    "text": bot_response["text"]
                },
                "action": {
                    "title": bot_response["text"],
                    "sections": [
                        {
                            "rows": self.BuildListButtons(bot_response["buttons"])
                        }
                    ]
                }
            }
        }
        template_url = "/whatsapp/1/message/interactive/list"
        return payload, template_url
    
    def BuildInteractiveButtons(self, buttons):
        print(f"Data for buttons: {buttons}")
        options = []
        for button in buttons:
            options.append({"type": "REPLY",
                            "id": button["payload"],
                            "title": button["title"]})
        
        return options

    def BuildListButtons(self, buttons):
        options = []
        for button in buttons:
            options.append({"id": button["payload"],
                            "title": button["title"],
                            "description": button["desc"]})

        return options
    