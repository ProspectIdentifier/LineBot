import json
import requests
import dialogflow
from decouple import config

from rest_framework.exceptions import APIException, ParseError

from google.oauth2 import service_account
import google.auth.transport.requests

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
                "text": msg,
		        "languageCode": config('LANGUAGECODE')
            }
        }
    }

    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + get_dialogflow_token()
    }

    url = config('DIALOGFLOWAPI')
    response = requests.post(url,
                        json=post_data,
                        headers=header)

    intent = json.loads(response.text)
    return intent.get("queryResult", None)

def handle_message(msg):
    try:
        intent = get_intent_from_dialogflow(msg.message.text)
        try:
            parsed_action = globals()[intent.get("action") + "ChatBotAction"](msg, intent)
            print(parsed_action)
            return parsed_action.get_response()
        except:
            return DefaultChatBotAction(msg, intent).get_response()
    except:
        return "I don't understand what you are saying."
