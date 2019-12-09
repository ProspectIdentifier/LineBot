from linebot.models import TextSendMessage, ConfirmTemplate, TemplateSendMessage, MessageAction
from dialogflowAPP.search_reseller import check_for_keyword_search
from dialogflowAPP.logrecoder import business_status, infra_status
from dialogflowAPP.models import BusinessLog, InfraLog

class DefaultChatBotAction():
    '''Default Reply'''
    def __init__(self, msg, intent, line_bot_api):
        self.msg = msg
        self.intent = intent
        self.line_bot_api = line_bot_api
        self.opp_msg = 'Opportunity is created! \
                        Do you need to reserve a meeting room with this customer?'

    def get_response(self):
        '''Get fulfillment text'''
        if 'action' in self.intent and self.intent['action'] == 'book_meeting.book_meeting-yes':
            business_status('book_meeting', self.msg.source.user_id)
            BusinessLog.objects.create(lineuserid=self.msg.source.user_id,
                                       action='book_meeting')

        if 'fulfillmentText' in self.intent and self.intent['fulfillmentText'] == self.opp_msg:
            confirm_template = ConfirmTemplate(text=self.opp_msg, actions=[
                MessageAction(label='Yes', text='Yes'),
                MessageAction(label='No', text='No'),
            ])
            template_message = TemplateSendMessage(
                alt_text='Opportunity is created!', template=confirm_template)
            self.line_bot_api.reply_message(self.msg.reply_token, template_message)
            return 'confirm_template'


        reseller_exist, reseller_info = check_for_keyword_search(self.intent, self.msg)
        if reseller_exist:
            self.line_bot_api.reply_message(self.msg.reply_token, reseller_info)
            return 'business end'

        response_msg = self.intent.get("fulfillmentText", "")
        if self.line_bot_api is not None:
            self.line_bot_api.reply_message(
                self.msg.reply_token,
                TextSendMessage(text=response_msg)
            )
        infra_status('chatbot_answer', self.msg.source.user_id)
        InfraLog.objects.create(action='chatbot_answer',
                                content=self.msg.source.user_id)
        return response_msg
