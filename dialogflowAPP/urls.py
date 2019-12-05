from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from dialogflowAPP import views

urlpatterns = [
    url(r'^api/chatbot/line/callback$', views.DialogflowAppChat.as_view(), name='dialogflow-app-chat'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
