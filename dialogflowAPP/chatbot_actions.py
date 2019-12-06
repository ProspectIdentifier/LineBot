from linebot.models import TextSendMessage

class DefaultChatBotAction():
    def __init__(self, msg, intent, line_bot_api):
        self.msg = msg
        self.intent = intent
        self.line_bot_api = line_bot_api

    def get_response(self):
        response_msg = self.intent.get("fulfillmentText", "")
        self.line_bot_api.reply_message(
            self.msg.reply_token,
            TextSendMessage(text=response_msg)
        )
        return response_msg

