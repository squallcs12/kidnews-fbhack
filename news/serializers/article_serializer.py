from rest_framework import serializers

from news.models import Article
from news.serializers.message_serializer import MessageSerializer


class ArticleSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, source='message_set')
    user_emotion = serializers.SerializerMethodField()

    def get_user_emotion(self, article):
        request = self.context['request']
        return article.get_user_emotion(request.user)

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'user', 'created_at', 'updated_at', 'messages', 'user_emotion', 'emotions',
                  'categories', 'quick_view_image', )
