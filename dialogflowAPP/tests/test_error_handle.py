import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..serializers import DialogflowAppSerializer

import responses
from decouple import config

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

# initialize the APIClient app
client = Client()

class TestLineBotApi(TestCase):
    """ Test module for inserting a new test """

    def setUp(self):
        import os
        enviroment = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[-1]

        if enviroment == 'staging':
            self.tested = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN_STG'))
        elif enviroment == 'production':
            self.tested = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN'))

        self.request_id = 'f70dd685-499a-4231-a441-f24b8d4fba21'
        self.headers = {'X-Line-Request-Id': self.request_id, 'HOGE': 'FUGA'}

    @responses.activate
    def test_error_handle(self):
        responses.add(
            responses.POST,
            LineBotApi.DEFAULT_API_ENDPOINT + '/v2/bot/message/push',
            json={
                "message": "Invalid reply token"
            },
            headers=self.headers,
            status=401
        )

        try:
            self.tested.push_message('to', TextSendMessage(text='hoge'))
        except LineBotApiError as e:
            self.assertEqual(e.status_code, 401)
            self.assertEqual(e.error.message, 'Invalid reply token')
            self.assertEqual(e.request_id, self.request_id)
            self.assertEqual(e.headers['HOGE'], 'FUGA')


    @responses.activate
    def test_error_handle_get_message_content(self):
        responses.add(
            responses.GET,
            LineBotApi.DEFAULT_API_DATA_ENDPOINT + '/v2/bot/message/1/content',
            json={
                "message": "Invalid reply token"
            },
            headers=self.headers,
            status=404
        )

        try:
            self.tested.get_message_content(1)
        except LineBotApiError as e:
            self.assertEqual(e.status_code, 404)
            self.assertEqual(e.error.message, 'Invalid reply token')
            self.assertEqual(e.request_id, self.request_id)
            self.assertEqual(e.headers['HOGE'], 'FUGA')
