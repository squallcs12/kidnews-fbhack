from django.views.generic.detail import DetailView

from news.models import Article


class ArticleContentView(DetailView):
    queryset = Article.objects.all()
    template_name = 'news/article/content.html'
