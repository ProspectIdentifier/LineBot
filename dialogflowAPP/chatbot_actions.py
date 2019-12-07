from linebot.models import TextSendMessage

class DefaultChatBotAction():
    '''Default Reply'''
    def __init__(self, msg, intent, line_bot_api):
        self.msg = msg
        self.intent = intent
        self.line_bot_api = line_bot_api

    def get_response(self):
        '''Get fulfillment text'''
        response_msg = self.intent.get("fulfillmentText", "")
        if self.line_bot_api is not None:
            self.line_bot_api.reply_message(
                self.msg.reply_token,
                TextSendMessage(text=response_msg)
            )
        return response_msg
