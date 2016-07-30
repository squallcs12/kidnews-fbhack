from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

from accounts.tests.intergrations.base import AccountTestBase


class SocialAccountTestBase(AccountTestBase):
    def init_social_app(self, provider):
        try:
            SocialApp.objects.get(provider=provider)
        except SocialApp.DoesNotExist:
            provider_upper = provider.upper()
            site = Site.objects.get()
            app = SocialApp.objects.create(provider=provider, name=provider,
                                           client_id=self.env('AUTH_{}_KEY'.format(provider_upper)),
                                           secret=self.env('AUTH_{}_SECRET'.format(provider_upper)))
            app.sites.add(site)
