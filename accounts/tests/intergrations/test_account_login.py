from django.core.urlresolvers import reverse

from common.tests.core import BaseLiveTestCase
from common.tests.factories.user_factory import UserFactory


class AccountLoginTestCase(BaseLiveTestCase):
    def login_with_info(self, **kwargs):
        self.user = UserFactory(**kwargs)
        self.visit_login_page()
        self.login(self.user)

    def assert_missing_field(self):
        self.assertIn(str(self.settings.LOGIN_URL), self.browser.current_url)
        self.should_see_text('This field is required')

    def test_show_login_view(self):
        self.visit(reverse('index'))
        self.link('Log in').click()

        self.until_current_url_contains(self.settings.LOGIN_URL)
        self.should_see_text('Log in with your website account')
        self.assertIsNotNone(self.label('Username'))
        self.assertIsNotNone(self.label('Password'))

    def test_login_with_valid_info(self):
        self.login_with_info()

    def test_login_without_username(self):
        self.login_with_info(username='')
        self.assert_missing_field()

    def test_login_without_password(self):
        self.login_with_info(password='')
        self.assert_missing_field()
