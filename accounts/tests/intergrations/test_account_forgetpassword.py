from django.core.urlresolvers import reverse

from accounts.tests.intergrations.base import AccountTestBase
from django.core import mail
from common.tests.factories.user_factory import UserFactory


class AccountForgetPasswordTestCase(AccountTestBase):
    def submit_forgetpassword_email(self, email):
        self.fill_in('#id_email', email)
        self.button('Reset My Password').click()

    def test_show_forgetpassword_view(self):
        self.visit_login_page()
        self.link('Forgot your password?').click()

        self.check_navigation_and_see_text(reverse('account_reset_password'), 'Password Reset')
        self.assertIsNotNone(self.label('E-mail'))

    def test_invalid_email(self):
        self.visit(reverse('account_reset_password'))
        invalid_email = [
            'abc'
            'abc@'
            'abc@d'
            '@abc'
        ]

        for email in invalid_email:
            self.submit_forgetpassword_email(email)
            # The page is not redirect
            self.assertIn(reverse('account_reset_password'), self.browser.current_url)

    def test_valid_unregistered_email(self):
        self.visit(reverse('account_reset_password'))
        self.submit_forgetpassword_email('abc@xyz.com')

        self.should_see_text('The e-mail address is not assigned to any user account')

    def test_valid_registered_email(self):
        self.visit(reverse('account_reset_password'))
        user = UserFactory()
        self.submit_forgetpassword_email(user.email)
        self.check_navigation_and_see_text(reverse('account_reset_password_done'),
                                           'We have sent you an e-mail. '
                                           'Please contact us if you do not receive it within a few minutes.')

        mail.outbox.should.have.length_of(1)
        mail.outbox[0].subject.should.contain('Password Reset')
