from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from news.views.article_viewset import ArticleViewSet

router = SimpleRouter()
router.register('articles', ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
