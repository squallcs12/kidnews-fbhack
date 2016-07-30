from accounts.tests.intergrations.social_base import SocialAccountTestBase


class AccountSocialLoginTestCase(SocialAccountTestBase):
    def setUp(self):
        self.visit_login_page()

    @classmethod
    def setUpClass(cls):
        with cls.in_environment(DJANGO_LIVE_TEST_SERVER_ADDRESS='localhost:8180'):
            super(AccountSocialLoginTestCase, cls).setUpClass()

    def social_login_by_provider(self, provider):
        self.init_social_app(provider=provider)

        self.find('#{provider}'.format(provider=provider)).click()
        self.until(lambda: '{provider}.com'.format(provider=provider) in self.browser.current_url)

    def test_login_facebook(self):
        self.social_login_by_provider('facebook')

        self.find('#loginbutton').should.be.ok

    def test_login_google(self):
        self.social_login_by_provider('google')

        self.should_see_text('Sign in with your Google Account')

    def test_twitter(self):
        self.social_login_by_provider('twitter')

        self.should_see_text('Authorize')
