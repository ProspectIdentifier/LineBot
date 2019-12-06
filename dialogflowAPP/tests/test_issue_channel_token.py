import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..serializers import DialogflowAppSerializer

import responses
from urllib import parse
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

        self.endpoint = LineBotApi.DEFAULT_API_ENDPOINT + '/v2/oauth/accessToken'
        self.access_token = "W1TeHCgfH2Liwa....."
        self.expires_in = 2592000
        self.token_type = "Bearer"
        self.client_id = 'client_id'
        self.client_secret = 'client_secret'

    @responses.activate
    def test_issue_line_token(self):
        responses.add(
            responses.POST,
            self.endpoint,
            json={
                "access_token": self.access_token,
                "expires_in": self.expires_in,
                "token_type": self.token_type
            },
            status=200
        )

        issue_access_token_response = self.tested.issue_channel_token(
            self.client_id,
            self.client_secret
        )

        request = responses.calls[0].request
        self.assertEqual('POST', request.method)
        self.assertEqual(self.endpoint, request.url)
        self.assertEqual('application/x-www-form-urlencoded', request.headers['content-type'])
        self.assertEqual(self.access_token, issue_access_token_response.access_token)
        self.assertEqual(self.expires_in, issue_access_token_response.expires_in)
        self.assertEqual(self.token_type, issue_access_token_response.token_type)

        encoded_body = parse.parse_qs(request.body)
        self.assertEqual('client_credentials', encoded_body['grant_type'][0])
        self.assertEqual(self.client_id, encoded_body['client_id'][0])
        self.assertEqual(self.client_secret, encoded_body['client_secret'][0])
