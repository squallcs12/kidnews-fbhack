from django.core.urlresolvers import reverse

from accounts.tests.intergrations.base import AccountTestBase
from common.tests.factories.user_factory import UserFactory


class AccountEditProfile(AccountTestBase):
    def test_visit_profile_without_login(self):
        self.visit(reverse('accounts:edit_profile'))
        self.until_current_url_contains(self.settings.LOGIN_URL)
        self.should_see_text('Log in with your website account')

    def visit_edit_profile(self):
        self.login_user()
        self.visit(reverse('accounts:edit_profile'))

    def test_show_edit_profile_view(self):
        self.visit_edit_profile()
        self.check_navigation_and_see_text(reverse('accounts:edit_profile'), 'Edit profile')

    def test_show_initial_profile(self):
        self.visit_edit_profile()

        self.find('#id_email').get_attribute('value').should.equal(self.user.email)
        self.find('#id_first_name').get_attribute('value').should.equal(self.user.first_name)
        self.find('#id_last_name').get_attribute('value').should.equal(self.user.last_name)

    def fill_email(self, email):
        self.fill_in('#id_email', email)
        self.button('Update profile').click()

    def test_change_invalid_email(self):
        self.visit_edit_profile()
        invalid_emails = ['abc@xyz', 'abc', 'xyz.com', ]

        for email in invalid_emails:
            self.fill_email(email)
            self.should_see_text('Enter a valid email address.')
            self.assertIn(reverse('accounts:edit_profile'), self.browser.current_url)

    def test_change_valid_profile(self):
        self.visit_edit_profile()
        new_user = UserFactory.build()
        self.fill_in('#id_email', new_user.email)
        self.fill_in('#id_first_name', new_user.first_name)
        self.fill_in('#id_last_name', new_user.last_name)
        self.button('Update profile').click()

        self.assertIn(reverse('accounts:profile'), self.browser.current_url)
