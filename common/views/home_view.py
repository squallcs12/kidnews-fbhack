from django.views.generic.base import TemplateView


class HomeView(TemplateView):
    template_name = "homepage.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['show_top_banner'] = True

        return context
