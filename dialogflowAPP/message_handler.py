import json
import requests
import dialogflow
from decouple import config

from rest_framework.exceptions import APIException, ParseError

from google.oauth2 import service_account
import google.auth.transport.requests

from linebot.models import TextSendMessage

from cachetools import cached, TTLCache
from dialogflowAPP.chatbot_actions import *

cache = TTLCache(maxsize=1024, ttl=3600)

@cached(cache)
def get_dialogflow_token():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            config('SERVICE_ACCOUNT_FILE'),
            scopes=config('SCOPES', cast=lambda v: [s.strip() for s in v.split(',')])
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        user_cred = { k: getattr(credentials, k) for k in ['token', 'valid'] }
    except Exception as e:
        raise APIException(e.args[0])
    return user_cred.get('token')


def get_intent_from_dialogflow(msg):
    post_data = {
        "queryInput":{
            "text":{
                "text": msg.message.text,
		        "languageCode": config('LANGUAGECODE')
            }
        }
    }

    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + get_dialogflow_token()
    }

    url = config('DIALOGFLOWAPI') + msg.source.user_id + ":detectIntent"
    response = requests.post(url,
                        json=post_data,
                        headers=header)

    intent = json.loads(response.text)
    return intent.get("queryResult", None)

def handle_message(msg, line_bot_api):
    try:
        intent = get_intent_from_dialogflow(msg)
        try:
            parsed_action = globals()[intent.get("action") + "ChatBotAction"](msg, intent, line_bot_api)
            return parsed_action.get_response()
        except:
            return DefaultChatBotAction(msg, intent, line_bot_api).get_response()
    except:
        err_msg = "I don't understand what you are saying."
        line_bot_api.reply_message(msg.reply_token, TextSendMessage(text=err_msg))
        return err_msg
