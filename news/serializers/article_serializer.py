from rest_framework import serializers

from news.models import Article
from news.serializers.message_serializer import MessageSerializer


class ArticleSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, source='message_set')

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'author', 'created_at', 'updated_at', 'messages')
