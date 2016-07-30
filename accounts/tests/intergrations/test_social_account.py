from django.core.urlresolvers import reverse

from accounts.tests.intergrations.social_base import SocialAccountTestBase
from common.tests.factories.social_app_factory import SocialAccountFactory


class SocialAccountTestCase(SocialAccountTestBase):
    def visit_social_list_view(self):
        self.visit_profile()
        self.click_account_menu_item('Social connection')
        self.until_current_url_contains(reverse('socialaccount_connections'))

    def test_show_social_view(self):
        self.login_user()
        self.visit_social_list_view()
        self.should_see_text('Account Connections')

    def test_button_add_social_account(self):
        self.init_social_app('google')
        self.login_user()
        self.visit_social_list_view()
        self.link('Google').click()
        self.should_see_text('Sign in with your Google Account')

    def test_show_social_account_list(self):
        self.login_user()
        social_accounts = SocialAccountFactory.create_batch(2, user=self.user)
        self.visit_social_list_view()
        for account in social_accounts:
            self.should_see_text(account.get_provider_account().__str__())
