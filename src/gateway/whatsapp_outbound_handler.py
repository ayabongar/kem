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
        
        # Ensure to always use the last response from the Bot [-1]
        if bot_responses[-1].get("text") is not None:
            data, templateUrl = self.BuildTextResponse(bot_responses[-1], bot_responses[-1]["recipient_id"])
        elif bot_responses[-1]["custom"].get("type") == "INTERACTIVE_LIST":
            data, templateUrl = self.BuildInteractiveList(bot_responses[-1]["custom"], bot_responses[-1]["recipient_id"])
        elif bot_responses[-1]["custom"].get("type") == "TEXT":
            data, templateUrl = self.BuildTextResponse(bot_responses[-1]["custom"], bot_responses[-1]["recipient_id"])

        print(f"Data for Infobip: {data}")

        asyncHttp = AsyncHTTPClient()
        asyncHttp.fetch(
            HTTPRequest(
                base_url + templateUrl,
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
            templateUrl = "/whatsapp/1/message/interactive/buttons"
        else:
            payload = {
                    "from": "447860099299",
                    "to": recipient_id,
                    "messageId": "a28dd97c-1ffb-4fcf-99f1-0b557ed381da",
                    "content": {
                        "text": bot_response["text"]
                    }
                }
            templateUrl = "/whatsapp/1/message/text"

        return payload, templateUrl
    
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
                    "title": "Choose an option",
                    "sections": [
                        {
                            "rows": self.BuildListButtons(bot_response["buttons"])
                        }
                    ]
                }
            }
        }
        templateUrl = "/whatsapp/1/message/interactive/list"
        return payload, templateUrl
    
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
    