# Create your views here.
from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ParseError, PermissionDenied

from .serializers import DialogflowAppSerializer
import dialogflowAPP.message_handler as msg_handler

from decouple import config
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import json

import os
enviroment = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[-1]

if enviroment == 'staging':
    line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN_STG'))
    handler = WebhookHandler(config('LINE_CHANNEL_SECRET_STG'))
elif enviroment == 'production':
    line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN'))
    handler = WebhookHandler(config('LINE_CHANNEL_SECRET'))


class DialogflowAppChat(views.APIView):
    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        response_data = { "message": "Hello, world!" }
        try:
            if signature == "DUMMY_SIGNATURE":
                #request from test script, not line, return full response
                response_msg = msg_handler.handle_message(json.loads(body), None)
                response_data = { "message": response_msg }
            else:
                #request from line
                events = handler.handle(body, signature)

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
        msg_handler.handle_message(event, line_bot_api)
