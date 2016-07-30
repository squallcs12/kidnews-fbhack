from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from news.views.article_comic_view import ArticleComicView
from news.views.article_content_view import ArticleContentView
from news.views.article_infographic_view import ArticleInfographicView
from news.views.article_viewset import ArticleViewSet

router = SimpleRouter()
router.register('articles', ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'articles/(?P<pk>\d+)/content', ArticleContentView.as_view(), name='article_content'),
    url(r'articles/(?P<pk>\d+)/infographic', ArticleInfographicView.as_view(), name='article_infographic'),
    url(r'articles/(?P<pk>\d+)/comic', ArticleComicView.as_view(), name='article_comic'),
]
