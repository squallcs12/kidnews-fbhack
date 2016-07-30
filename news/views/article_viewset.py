from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from news.models import Article, Message, UserEmotion, Art
from news.serializers.art_serializer import ArtSerializer
from news.serializers.article_serializer import ArticleSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['POST'])
    def messages(self, request, pk):
        """
        @param request:
        @param pk:
        @return:
        ---
        request_serializer: rest_framework.serializers.Serializer
        parameters:
            - name: content
              required: true
        """
        article = self.get_object()
        message_text = request.data['content']
        message = Message.objects.create(user=request.user, content=message_text, article=article, to_user=article.user)

        return Response({
            'success': True,
        })

    @detail_route(methods=['POST'])
    def emotion(self, request, pk):
        """

        @param request:
        @param pk:
        @return:
        ---
        serializer: news.serializers.emotion_serializer.EmotionSerializer
        """
        article = self.get_object()
        emotion = int(request.data['emotion'])
        user_emotion, created = UserEmotion.objects.get_or_create(user=request.user,
                                                                  article=article,
                                                                  defaults={
                                                                      'emotion': emotion
                                                                  })
        if not created:
            user_emotion.delete()
            if user_emotion.emotion != emotion:
                UserEmotion.objects.create(user=request.user, article=article, emotion=emotion)
        return Response({
            'emotions': article.emotions(),
            'user_emotion': emotion,
        })

    @detail_route(methods=['POST'])
    def art(self, request, pk):
        """

        @param request:
        @param pk:
        @return:
        ---
        serializer: news.serializers.art_serializer.ArtSerializer
        parameters:
            - name: picture
              type: file
              required: true
        """
        article = self.get_object()
        user_art, created = Art.objects.get_or_create(user=request.user, article=article)
        serializer = ArtSerializer(instance=user_art, data=request.data, context={
            'request': request,
        })
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data)
