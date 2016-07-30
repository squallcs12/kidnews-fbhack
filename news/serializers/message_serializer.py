from rest_framework import serializers

from news.models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'content', 'article', 'user', 'created_at')
