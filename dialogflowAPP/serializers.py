from rest_framework import serializers

class DialogflowAppSerializer(serializers.Serializer):
    '''Your data serializer, define your fields here.'''
    message = serializers.CharField()
