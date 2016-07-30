from django.conf import settings
from django.views.generic.base import TemplateView


class LoginView(TemplateView):
    template_name = 'accountkit/login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)

        context['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
        context['ACCOUNT_KIT_API_VERSION'] = settings.ACCOUNT_KIT_API_VERSION
        return context
