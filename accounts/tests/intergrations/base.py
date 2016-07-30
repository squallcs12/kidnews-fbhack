from django.core.urlresolvers import reverse

from common.tests.core import BaseLiveTestCase


class FillPasswordFormMixin:
    def fill_password(self, password, confirm_password):
        self.fill_in('#id_password1', password)
        self.fill_in('#id_password2', confirm_password)


class AccountTestBase(BaseLiveTestCase):
    def visit_profile(self):
        self.visit(reverse('accounts:profile'))

    def click_account_menu_item(self, text):
        if not self.link(text).is_displayed():
            self.link('Expand all').click()
            self.until(lambda: self.link(text).is_displayed())
        self.link(text).click()

    def check_navigation_and_see_text(self, path, message):
        self.until(lambda: self.assertIn(path, self.browser.current_url))
        self.should_see_text(message)
