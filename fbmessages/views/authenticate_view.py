from django.views.generic.base import TemplateView


class AuthenticateView(TemplateView):
    template_name = 'fbmessages/login.html'
