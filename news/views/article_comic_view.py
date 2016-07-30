from django.views.generic.detail import DetailView

from news.models import Article


class ArticleComicView(DetailView):
    queryset = Article.objects.all()
    template_name = 'news/article/comic.html'
