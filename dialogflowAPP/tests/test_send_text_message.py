import os
import json
from django.test import TestCase, Client

import responses
from decouple import config

from linebot import LineBotApi
from linebot.models import TextSendMessage

# initialize the APIClient app
CLIENT = Client()

class TestLineBotApi(TestCase):
    """ Test module for inserting a new test """

    def setUp(self):
        enviroment = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[-1]

        if enviroment == 'staging':
            self.tested = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN_STG'))
        elif enviroment == 'production':
            self.tested = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN'))

        # test data
        self.text_message = TextSendMessage(text='Hello, world')
        self.message = [{"type": "text", "text": "Hello, world"}]

    @responses.activate
    def test_reply_text_message(self):
        '''test line reply message'''
        responses.add(
            responses.POST,
            LineBotApi.DEFAULT_API_ENDPOINT + '/v2/bot/message/reply',
            json={}, status=200
        )

        self.tested.reply_message('replyToken', self.text_message)

        request = responses.calls[0].request
        self.assertEqual(
            request.url,
            LineBotApi.DEFAULT_API_ENDPOINT + '/v2/bot/message/reply')
        self.assertEqual(request.method, 'POST')
        self.assertEqual(
            json.loads(request.body),
            {
                "replyToken": "replyToken",
                'notificationDisabled': False,
                "messages": self.message
            }
        )
