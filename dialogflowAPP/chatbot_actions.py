from linebot.models import TextSendMessage
from dialogflowAPP.search_reseller import check_for_keyword_search
from dialogflowAPP.logrecoder import *
import traceback

class DefaultChatBotAction():
    '''Default Reply'''
    def __init__(self, msg, intent, line_bot_api):
        self.msg = msg
        self.intent = intent
        self.line_bot_api = line_bot_api

    def get_response(self):
        '''Get fulfillment text'''
        try:
            if self.intent['action'] == 'book_meeting.book_meeting-yes':
                business_status('book_meeting', self.msg.source.user_id)
        except:
            pass

        reseller_exist, reseller_info = check_for_keyword_search(self.intent)
        if reseller_exist:
            application_status('reseller_search', self.msg.source.user_id)
            line_bot_api.reply_message(self.msg.reply_token, reseller_info)
            return 'business end'

        response_msg = self.intent.get("fulfillmentText", "")
        if self.line_bot_api is not None:
            self.line_bot_api.reply_message(
                self.msg.reply_token,
                TextSendMessage(text=response_msg)
            )
        error_status(traceback.format_exc(), self.msg.source.user_id)
        return response_msg
