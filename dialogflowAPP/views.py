# Create your views here.
from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ParseError, PermissionDenied

from .serializers import DialogflowAppSerializer
import dialogflowAPP.message_handler as msg_handler
# import dialogflowAPP.model as model

from decouple import config
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(config('LINE_CHANNEL_SECRET'))

class DialogflowAppChat(views.APIView):
    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = handler.handle(body, signature)

        except InvalidSignatureError:
            raise PermissionDenied()

        except LineBotApiError:
            raise ParseError()

        serializer = DialogflowAppSerializer(data={"message": "Hello, world!"})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handler.add(MessageEvent, message=TextMessage)
    def message_text(event: MessageEvent):
        msg_handler.handle_message(event, line_bot_api)
        
