import json
import requests
from decouple import config

from rest_framework.exceptions import APIException

from google.oauth2 import service_account
import google.auth.transport.requests

from cachetools import cached, TTLCache
from linebot.models import TextSendMessage

from dialogflowAPP.chatbot_actions import *

from dialogflowAPP.search_reseller import check_for_keyword_search
from dialogflowAPP.logrecoder import *

cache = TTLCache(maxsize=1024, ttl=3600)

@cached(cache)
def get_dialogflow_token():
    '''Get google token'''
    try:
        service_account_info = google_service_account_info()
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=config('SCOPES', cast=lambda v: [s.strip() for s in v.split(',')])
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        user_cred = {k: getattr(credentials, k) for k in ['token', 'valid']}
    except Exception as error:
        raise APIException(error.args[0])
    return user_cred.get('token')

def google_service_account_info():
    '''Google service account private key JSON file'''
    service_account_info = dict()
    service_account_info['type'] = config('GOOGLE_TYPE')
    service_account_info['project_id'] = config('GOOGLE_PROJECT_ID')
    service_account_info['private_key_id'] = config('GOOGLE_PRIVATE_KEY_ID')
    service_account_info['private_key'] = config('GOOGLE_PRIVATE_KEY').replace("\\n", "\n")
    service_account_info['client_email'] = config('GOOGLE_CLIENT_EMAIL')
    service_account_info['client_id'] = config('GOOGLE_CLIENT_ID')
    service_account_info['auth_uri'] = config('GOOGLE_AUTH_URI')
    service_account_info['token_uri'] = config('GOOGLE_TOKEN_URI')
    service_account_info['auth_provider_x509_cert_url'] = config('GOOGLE_AUTH_PROVIDER_X509_CERT_URL')
    service_account_info['client_x509_cert_url'] = config('GOOGLE_CLIENT_X509_CERT_URL')
    return service_account_info

def get_intent_from_dialogflow(msg_text, user_id):
    '''Get intent from dialogflow'''
    post_data = {
        "queryInput":{
            "text":{
                "text": msg_text,
                "languageCode": config('LANGUAGECODE')
            }
        }
    }

    header = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + get_dialogflow_token()
    }

    url = config('DIALOGFLOWAPI') + user_id + ":detectIntent"
    response = requests.post(url,
                             json=post_data,
                             headers=header)

    intent = json.loads(response.text)
    return intent.get("queryResult", None)

def handle_message(msg, line_bot_api):
    '''Line message handle'''
    try:
        infra_status('user_access', msg.source.user_id)
        #i dont know if there's better solution for this
        if line_bot_api is None: #is testing
            intent = get_intent_from_dialogflow(msg["message"]["text"], msg["source"]["user_id"])
        else: #is from LINE
            intent = get_intent_from_dialogflow(msg.message.text, msg.source.user_id)

        try:
            if intent['intent']['displayName'] == 'book_meeting':
                business_status('book_meeting', msg.source.user_id)
        except TypeError:
            pass

        try:
            reseller_exist, reseller_info = check_for_keyword_search(intent)
            if reseller_exist:
                application_status('reseller_search', msg.source.user_id)
                line_bot_api.reply_message(msg.reply_token, reseller_info)
                return 'business end'
            parsed_action = globals()[intent.get("action") + "ChatBotAction"](msg, intent, line_bot_api)
            return parsed_action.get_response()
        except:
            return DefaultChatBotAction(msg, intent, line_bot_api).get_response()

    except Exception as error:
        print(error)
        err_msg = "I don't understand what you are saying."
        if line_bot_api is not None:
            line_bot_api.reply_message(msg.reply_token, TextSendMessage(text=err_msg))
        return err_msg
