import requests
import json
from decouple import config

FAKE_MESSAGE = "hello"

webhook_url = config("WEBHOOK_URL")
#https://[heroku-app].herokuapp.com/api/chatbot/line/callback
headers = {
    "X_LINE_SIGNATURE": "DUMMY_SIGNATURE"
}
post_data = {
    "type": "message",
    "replyToken": "DUMMY",
    "source": {
        "user_id": "DUMMY",
        "type": "user"
    },
    "timestamp": 1000000000,
    "message": {
        "type": "text",
        "id": "DUMMY",
        "text": FAKE_MESSAGE
    }
}

res = requests.post(webhook_url, json=post_data, headers=headers)

response_msg = json.loads(res.text).get("message")

default_messages = [
    "Hi! How are you doing?",
    "Hello! How can I help you?",
    "Good day! What can I do for you today?",
    "Greetings! How can I assist?"
]

is_correct = False
for msg in default_messages:
    if msg == response_msg:
        is_correct = True

if not is_correct:
    raise "Test failed"
else:
    print("passed")