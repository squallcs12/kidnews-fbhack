from django.views.generic.detail import DetailView

from news.models import Article


class ArticleInfographicView(DetailView):
    queryset = Article.objects.all()
    template_name = 'news/article/infographic.html'
