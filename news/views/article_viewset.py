from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from news.models import Article, Message
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
        message = Message.objects.create(user=request.user, content=message_text, article=article)
        return Response({
            'success': True,
        })
