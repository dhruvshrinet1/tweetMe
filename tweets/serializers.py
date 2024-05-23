from django.conf import settings
from rest_framework import serializers
from .models import Tweet

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['content']

    def validate_content(self,value):
        if len(value) > settings.MAX_LENGTH:
            raise serializers.ValidationError('Tweet is too long')
        return value
