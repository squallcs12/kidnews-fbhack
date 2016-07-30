from rest_framework import serializers

from news.models import Article
from news.serializers.message_serializer import MessageSerializer


class ArticleSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, source='message_set')
    user_emotion = serializers.SerializerMethodField()
    user_art = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_user_emotion(self, article):
        request = self.context['request']
        return article.get_user_emotion(request.user)

    def get_user_art(self, article):
        request = self.context['request']
        return self.build_absolute_uri(article.get_user_art(request.user))

    def build_absolute_uri(self, url):
        request = self.context['request']
        return request.build_absolute_uri(url)

    def get_content(self, article):
        return self.build_absolute_uri(article.get_content_link())

    def get_infographic_link(self, article):
        if article.infographic:
            return self.build_absolute_uri(article.get_infographic_link())

    def get_comic_link(self, article):
        if article.comic:
            return self.build_absolute_uri(article.get_comic_link())

    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'user', 'created_at', 'updated_at', 'messages', 'user_emotion', 'emotions',
                  'categories', 'quick_view_image',
                  'question', 'answer', 'infographic', 'comic', 'user_art')
