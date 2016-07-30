from django.core.urlresolvers import reverse

from accounts.tests.intergrations.base import AccountTestBase, FillPasswordFormMixin


class AccountChangePasswordTestCase(FillPasswordFormMixin, AccountTestBase):
    def setUp(self):
        self.login_user()

    def submit_change_password_form(self, old_pw, new_pw, confirm_pw):
        self.fill_in('#id_oldpassword', old_pw)
        self.fill_password(new_pw, confirm_pw)
        self.button('Change Password').click()

    def test_show_changepassword_view(self):
        self.visit_profile()
        self.click_account_menu_item('Change password')
        self.check_navigation_and_see_text(reverse('account_change_password'), 'Change Password')

    def test_wrong_old_password(self):
        self.visit(reverse('account_change_password'))

        self.submit_change_password_form('invalid', '123', '123')
        self.should_see_text('Please type your current password.')

    def assert_password_validation(self, password, confirm_password, message):
        self.visit(reverse('account_change_password'))

        self.submit_change_password_form(self.user.raw_password, password, confirm_password)
        self.should_see_text(message)

    def test_new_password_not_match(self):
        self.assert_password_validation('abcABC123!', 'abcABC', 'You must type the same password each time.')

    def test_new_password_weak(self):
        self.assert_password_validation('123', '123', 'Password must be a minimum of 6 characters.')

    def test_change_password_success(self):
        self.assert_password_validation('abcdABC123!', 'abcdABC123!', 'Password successfully changed.')
