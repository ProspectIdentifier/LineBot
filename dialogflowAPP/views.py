import os
import json
from decouple import config

# Create your views here.
from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, PermissionDenied

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage

import dialogflowAPP.message_handler as msg_handler
from .serializers import DialogflowAppSerializer

ENVIROMENT = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[-1]

if ENVIROMENT == 'staging':
    line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN_STG'))
    handler = WebhookHandler(config('LINE_CHANNEL_SECRET_STG'))
elif ENVIROMENT == 'production':
    line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN'))
    handler = WebhookHandler(config('LINE_CHANNEL_SECRET'))


class DialogflowAppChat(views.APIView):
    '''Send Message to Dialogflow from Line Message API'''
    def post(self, request, *args, **kwargs):
        '''POST Action'''
        signature = request.META['HTTP_X_LINE_SIGNATURE']

        body = request.body.decode('utf-8')
        response_data = {"message": "Hello, world!"}
        try:
            if signature == "DUMMY_SIGNATURE":
                #request from test script, not line, return full response
                response_msg = msg_handler.handle_message(json.loads(body), None)
                response_data = {"message": response_msg}
            else:
                #request from line
                handler.handle(body, signature)

        except InvalidSignatureError:
            raise PermissionDenied()

        except LineBotApiError:
            raise ParseError()

        serializer = DialogflowAppSerializer(data=response_data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handler.add(MessageEvent, message=TextMessage)
    def message_text(event: MessageEvent):
        '''Message Handle'''
        msg_handler.handle_message(event, line_bot_api)
