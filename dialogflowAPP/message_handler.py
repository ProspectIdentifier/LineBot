import json
from datetime import datetime, timedelta
import traceback
import psutil
import requests

from decouple import config

from rest_framework.exceptions import APIException

from google.oauth2 import service_account
import google.auth.transport.requests

from cachetools import cached, TTLCache
from linebot.models import TextSendMessage

from dialogflowAPP.chatbot_actions import *
from dialogflowAPP.logrecoder import infra_status, error_status
from dialogflowAPP.models import InfraLog

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

last_time = datetime.now()

def handle_message(msg, line_bot_api):
    '''Line message handle'''
    try:
        global last_time
        infra_status('user_access', msg.source.user_id)
        InfraLog.objects.create(action='user_access',
                                content=msg.source.user_id)

        if datetime.now() - last_time > timedelta(seconds=10):
            infra_status('cpu_percent', str(psutil.cpu_percent()))
            InfraLog.objects.create(action='cpu_percent',
                                    content=str(psutil.cpu_percent()))

            infra_status('virtual_memory', str(psutil.virtual_memory()))
            InfraLog.objects.create(action='virtual_memory',
                                    content=str(psutil.virtual_memory()))
            last_time = datetime.now()
        #i dont know if there's better solution for this
        if line_bot_api is None: #is testing
            intent = get_intent_from_dialogflow(msg["message"]["text"], msg["source"]["user_id"])
        else: #is from LINE
            intent = get_intent_from_dialogflow(msg.message.text, msg.source.user_id)
        return DefaultChatBotAction(msg, intent, line_bot_api).get_response()

    except Exception as error:
        print(error)
        err_msg = "I don't understand what you are saying."
        if line_bot_api is not None:
            line_bot_api.reply_message(msg.reply_token, TextSendMessage(text=err_msg))
            error_status(traceback.format_exc(), msg.source.user_id)
        return err_msg
