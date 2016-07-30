from django.core.urlresolvers import reverse

from accounts.tests.intergrations.base import AccountTestBase


class TwoFactorTestCase(AccountTestBase):
    def setUp(self):
        self.login_user()

    def test_visit_two_factor_setting(self):
        self.visit_profile()
        self.click_account_menu_item('Two-factor settings')
        self.until_current_url_contains(reverse('two_factor:profile'))
