import json
import os
import threading
import time
import django
import django_nose
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.core.urlresolvers import reverse
from django.test.testcases import LiveServerTestCase, SimpleTestCase as DjangoSimpleTestCase
from django_nose.plugin import ResultPlugin, DjangoSetUpPlugin, TestReorderer
from django_nose.runner import _get_plugins_from_settings
from faker import Faker
from nose.core import TestProgram, TextTestRunner
from nose.result import TextTestResult
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
import sure  # need for sure style assertion

from common.tests.factories.user_factory import UserFactory

User = get_user_model()

fake = Faker()

# Make shortcut for popular used
WebElement.find = WebElement.find_element_by_css_selector
WebElement.find_all = WebElement.find_elements_by_css_selector
WebElement.xpath = WebElement.find_element_by_xpath


def element_by_tagname_and_text(self, tag, text):
    """
    Find element by tag name and content
    @param self: WebElement
    @type self: WebElement
    @param tag: tag name
    @type tag: str
    @param text: content
    @type text: str
    @return: WebElement
    """
    _xpath = ".//%s[normalize-space(.)='%s']" % (tag, text)
    try:
        return self.find_element_by_xpath(_xpath)
    except NoSuchElementException:
        pass
    return False


WebElement.element_by_tagname_and_text = element_by_tagname_and_text


def button(self, text):
    """
    Find button element by content
    @param self: WebElement
    @type self: WebElement
    @param text: content
    @type" str
    @return: WebElement
    """
    return self.element_by_tagname_and_text("button", text)


WebElement.button = button


"""prepare for with statement style
so we can write like this
with WebElement.button(text) as button:
    button.click()
"""


def _exit(self, type, value, traceback):
    return


WebElement.__enter__ = lambda x: x
WebElement.__exit__ = _exit


def select_by_visible_text(self, text):
    Select(self).select_by_visible_text(text)


WebElement.select_by_visible_text = select_by_visible_text


def has_class(self, value):
    """
    Shortcut for checking an element has class name or not
    @param self: WebElement
    @param self: WebElement
    @param value: class name
    @type value: str
    @return: bool
    """
    return value in self.get_attribute('class')


WebElement.has_class = has_class


class TimeoutException(AssertionError):
    """Custom exception for self.until
    """
    pass

"""Init global object for each run"""
world = threading.local()
world.browser = None
world.browsers = []


class UserTestBaseMixin(object):
    """Base class contain step for user login"""
    user = None

    def login(self, user):
        raise NotImplemented()

    def init_user(self):
        """
        Create user object
        @return: common.models.User
        """
        user = UserFactory()
        if self.user is None:
            self.user = user
        return user

    def login_user(self, user=None):
        """
        Login user to current context
        @param user: user need to login
        @type user: common.models.User
        @return: None
        """
        if user is None:
            if self.user is None:
                self.init_user()
            user = self.user
        self.login(user)


class TestDescriptionOverride:
    """
    Class override test case description for django nose
    """
    def __str__(self):
        """
        Return in format <module>:<class>.<method> so we can run individual test easier
        @return: str
        """
        return "{module}:{klass}.{method}".format(
            module=self.__class__.__module__,
            klass=self.__class__.__name__,
            method=self._testMethodName,
        )


class ChangeBrowserContext:
    """
    Switch between multiple browser context, will be used in with statement
    """
    def __init__(self, browser):
        self.browser = world.browser
        self.new_browser = browser

    def __enter__(self):
        world.browser = self.new_browser

    def __exit__(self, type, value, traceback):
        world.browser = self.browser


class InEnvironmentContext:
    def __init__(self, **kwargs):
        self.old_environ = os.environ.copy()
        self.kwargs = kwargs

    def __enter__(self):
        os.environ.update(self.kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ = self.old_environ


class BaseLiveTestCase(TestDescriptionOverride, LiveServerTestCase, UserTestBaseMixin):
    source = 0  # class counter
    source_dir = os.environ.get('CIRCLE_ARTIFACTS')  # get circle ci artifacts folder
    terminate_test_server_after_test = False
    """Skip tear down class method, this will keep the server thread open until the test end
    But it also will reduce about 5 seconds when switching test class"""

    @classmethod
    def close_browsers(cls):
        """
        Close all opening browsers
        @return: None
        """
        for browser in world.browsers:
            try:
                browser.quit()
            except WebDriverException:
                pass
        world.browsers = []
        world.browser = None

    def init_firefox(self):
        """
        Init firefox browser
        @return: webdriver.Firefox
        """
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('media.navigator.permission.disabled', True)
        firefox_profile.set_preference('dom.disable_beforeunload', True)
        firefox_profile.update_preferences()

        browser = webdriver.Firefox(firefox_profile)
        browser.implicitly_wait(10)
        browser.set_window_size(width=1200, height=800)

        return browser

    def init_phantomjs(self):
        """
        Init phantomJS browser
        @return: webdriver.PhantomJS
        """
        return webdriver.PhantomJS()

    def init_browser(self):
        if os.environ.get('BROWSER') == 'phantomjs':
            browser = self.init_phantomjs()
        else:
            browser = self.init_firefox()
        world.browsers.append(browser)
        return browser

    def in_browser(self, browser):
        return ChangeBrowserContext(browser)

    @property
    def browser(self):
        """
        @return: selenium.webdriver.remote.webdriver.WebDriver
        """
        if world.browser is None:
            world.browser = self.init_browser()
        return world.browser

    @classmethod
    def setUpClass(cls):
        """
        Init class
        @return: None
        """
        if not hasattr(LiveServerTestCase, 'static_collected') or not LiveServerTestCase.static_collected:
            # collect static for live server test case automatically
            management.call_command('collectstatic', interactive=False, verbosity=0)
            LiveServerTestCase.static_collected = True
        super(BaseLiveTestCase, cls).setUpClass()

    @classmethod
    def _tearDownClassInternal(cls):
        if cls.terminate_test_server_after_test:
            super(BaseLiveTestCase, cls)._tearDownClassInternal()

    def visit(self, page):
        """
        Shortcut selenium.WebDriver.get
        @param page: url without domain
        @type page: str
        @return: None
        """
        self.browser.get('{root}{path}'.format(root=self.live_server_url, path=page))

    def should_see_text(self, text):
        """
        Asserting text appear in body
        @param text: text should appear
        @return: None
        @raise AssertionError
        """
        if not isinstance(text, str):
            text = str(text)
        self.assertIn(text, self.find('body').text)

    def should_see_texts(self, texts):
        """
        Asserting many texts should appear in body
        @param texts: array of text
        @type texts: list
        @return: None
        @raise AssertionError
        """
        body_text = self.find('body').text
        texts = [str(x) for x in texts]
        for text in texts:
            body_text.should.contain(text)

    def should_see_one_among_texts(self, texts):
        """
        Asserting one of texts should appear
        @param texts: array of text
        @type texts: list
        @return: None
        @raise AssertionError
        """
        body_text = self.find("body").text
        found = any(str(x) in body_text for x in texts)
        found.should.be.true

    def should_not_see_text(self, text):
        """
        Assert text should not appear in body
        @param text: text should not appear
        @type text: str
        @return: None
        @raise AssertionError
        """
        self.assertNotIn(text, self.find('body').text)

    def visit_login_page(self):
        self.visit(settings.LOGIN_URL)

    def login(self, user):
        """
        Login user into system using browser
        @param user: user need to be log in
        @type user: common.models.User
        @return: None
        """
        self.visit_login_page()
        self.find("#id_auth-username").send_keys(user.username)
        self.find("#id_auth-password").send_keys(user.raw_password)
        self.button("Next").click()
        self.until(lambda: self.browser.page_source.should.contain(user.username))  # login successfully

    def logout(self):
        """
        Logout user
        @return: None
        """
        self.visit(reverse('logout'))

    def element_exist(self, css_selector):
        """
        Check if element exists in DOM
        @param css_selector: css selector
        @type css_selector: str
        @return: bool
        """
        try:
            self.find(css_selector)
            return True
        except NoSuchElementException:
            return False

    def element_by_tagname_and_text(self, tag, text, parent="body"):
        """
        Find element by tagname and text
        @param tag: Html tag
        @type tag: str
        @param text: Element content
        @type text: str
        @param parent: Parent node
        @type parent: str
        @return: WebElement or False
        """
        _xpath = ".//%s[normalize-space(.)='%s']" % (tag, text)
        for node in self.find_all(parent):
            try:
                return node.xpath(_xpath)
            except NoSuchElementException:
                pass
        return False

    def element_by_classname_and_text(self, class_name, text, parent="body"):
        """
        Find element by classname and text
        @param class_name: Element class name
        @type class_name: str
        @param text: Element content
        @type text: str
        @param parent: Parent node
        @type parent: str
        @return: WebElement or False
        """
        _xpath = ".//*[contains(@class, '%s')][normalize-space(.)='%s']" % (class_name, text)
        for node in self.find_all(parent):
            try:
                return node.xpath(_xpath)
            except NoSuchElementException:
                pass
        return False

    def button(self, button_text, parent="body"):
        """
        Find button by text
        @param button_text: Button content
        @type button_text: str
        @param parent: Parent node
        @type parent: str
        @return: WebElement or False
        """
        return self.element_by_tagname_and_text("button", button_text, parent)

    def link(self, label_text, parent="body"):
        """
        Find link by text
        @param label_text: Link content
        @type label_text: str
        @param parent: Parent node
        @type parent: str
        @return: WebElement or False
        """
        return self.element_by_tagname_and_text("a", label_text, parent)

    def label(self, label_text, parent="body"):
        """
        Find label by text
        @param label_text: Label content
        @type label_text: str
        @param parent: Parent node
        @type parent: str
        @return: WebElement or False
        """
        return self.element_by_tagname_and_text("label", label_text, parent)

    def element_for_label(self, label):
        """
        Find form element base on label text
        @param label:
        @return: WebElement
        """
        if isinstance(label, str):
            label = self.label(label)
        return self.find("#%s" % label.get_attribute("for"))

    def find_all(self, selector):
        return self.browser.find_elements_by_css_selector(selector)

    def find(self, selector):
        """
        Find element by css selector
        @param selector: css elector
        @type selector: str
        @return: WebElement
        """
        try:
            return self.browser.find_element_by_css_selector(selector)
        except NoSuchElementException:
            if self.source_dir:  # on circle ci only
                BaseLiveTestCase.source += 1
                # save source code to artifact folder
                with open("%s/current_html_%s.html" % (self.source_dir, BaseLiveTestCase.source), "w") as f:
                    f.write(selector)
                    f.write("\r\n")
                    f.write(self.browser.page_source)
            raise  # continue raising exception

    @classmethod
    def take_screen_shot(cls, folder=None):
        """
        Take screenshot for all opening browsers
        @param folder: save in folder name
        @type folder: str
        @return: None
        """
        if cls.source_dir:  # only on cirle ci
            BaseLiveTestCase.source += 1
            if folder is None:
                folder = BaseLiveTestCase.source
            dir_path = os.path.join(cls.source_dir, str(folder))
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
            for index, browser in enumerate(world.browsers):
                filename = os.path.join(dir_path, "current_page_{index}.png".format(index=index))
                print(filename)
                browser.get_screenshot_as_file(filename)

    def fill_in(self, selector, value):
        """
        Filling text into input element
        @param selector: css selector
        @type selector: str
        @param value: input value
        @type value: str
        @return: None
        """
        selector_input = self.find(selector)
        selector_input.clear()
        selector_input.send_keys(value)

    def sleep(self, seconds):
        """
        Sleep the process to wait for the result
        @param seconds: time to wait in second
        @type seconds: int
        @return: None
        """
        time.sleep(seconds)

    def until(self, method, timeout=10, message='', interval=0.5):
        """
        Calls the method provided with the driver as an argument until the return value is not False.
        @param method: method that check for expected result
        @type method: function
        @param timeout: maximum running time in seconds
        @type timeout: int
        @param message: error message
        @type message: str
        @param interval: sleep duration between each check
        @return: None
        @raise TimeoutException
        """
        end_time = time.time() + timeout
        error = None
        while True:
            try:
                value = method()
                if value or value is None:
                    return value
            except Exception as ex:
                if error:
                    try:
                        raise ex from error
                    except Exception as ex2:
                        error = ex2
                else:
                    error = ex
            time.sleep(interval)
            if time.time() > end_time:
                break
        self.take_screen_shot()
        raise TimeoutException(message) from error

    def is_displayed_in_viewport(self, element):
        """
        Check if an element is displayed on current view port. For now check against only y-position
        @param element: element to be checked
        @type element: WebElement
        @return: bool
        """
        if isinstance(element, str):
            element = self.find(element)

        element_location = element.location
        viewport_y = self.browser.execute_script("return window.scrollY")
        viewport_height = self.browser.execute_script("return window.innerHeight")

        return viewport_y + viewport_height >= element_location['y'] >= viewport_y

    def ajax_complete(self):
        """
        Check if ajax call is complete
        @return: bool
        """
        return 0 == self.browser.execute_script("return jQuery.active")

    def get_js_var(self, var_name):
        """
        Get javascript variable value
        @param var_name: variable name
        @type var_name: str
        @return: value
        """
        return self.browser.execute_script("return {var_name}".format(var_name=var_name))

    def until_ajax_complete(self):
        """
        Wait for ajax call to complete
        @return: None
        @raise TimeoutException
        """
        self.until(self.ajax_complete)

    def until_current_url_contains(self, url):
        self.until(lambda: str(url) in self.browser.current_url)

    @property
    def settings(self):
        return settings

    @staticmethod
    def env(name, default=None):
        return settings.ENV(name, default=default)

    @staticmethod
    def in_environment(**kwargs):
        return InEnvironmentContext(**kwargs)


class SimpleTestCase(TestDescriptionOverride, DjangoSimpleTestCase, UserTestBaseMixin):
    response = None
    _soup = None

    @property
    def soup(self):
        """
        Parse html content by BeautifulSoup
        @return: BeautifulSoup
        """
        if self._soup is None:
            self._soup = BeautifulSoup(self.response.content)
        return self._soup

    def login(self, user):
        """
        Login user
        @param user: user to be log in
        @type user: common.models.User
        @return: None
        """
        self.client.login(username=user.username, password=user.raw_password)

    def visit(self, path, *args, **kwargs):
        """
        GET request from view
        @param path: path to view without host
        @type path: str
        @param args: extra args
        @type args: list
        @param kwargs: extra kwargs
        @type kwargs: dict
        @return: None
        """
        self.response = self.client.get(path, *args, **kwargs)
        self._soup = None

    def find_all(self, selector):
        """
        Find all elements from response
        @param selector: css selector
        @type selector: str
        @return: bs4.element.Tag
        """
        return self.soup.select(selector)

    def link(self, text):
        """
        Find link element by content
        @param text: link content
        @type text: str
        @return: bs4.element.Tag
        """
        return self.soup.find('a', text=text)

    def should_see_text(self, text):
        """
        Assert text is appear in response
        @param text: text expected to appear
        @type text: str
        @return: None
        @raise AssertionError
        """
        self.soup.text.should.contain(text)

    def should_not_see_text(self, text):
        """
        Assert text is not appear in response
        @param text: text not expected to appear
        @type text: str
        @return: None
        @raise AssertionError
        """
        self.soup.text.shouldnt.contain(text)

    def json(self, response):
        """
        Parse response content into json format
        @param response: response object
        @type response: django.http.response
        @return: json string
        """
        return json.loads(response.content.decode())

    def should_see_texts(self, texts):
        """
        Assert texts are appear in response
        @param texts: texts expected to appear
        @type texts: list
        @return: None
        @raise AssertionError
        """
        for text in texts:
            self.soup.text.should.contain(text)


class DjangoNoseTextTestResult(TextTestResult):
    def addError(self, test, err):
        """
        Custom addError to take screenshot when error occurs
        """
        BaseLiveTestCase.take_screen_shot(test.test._testMethodName)
        super(DjangoNoseTextTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        """
        Custom addFailure to take screenshot when failure occurs
        """
        BaseLiveTestCase.take_screen_shot(test.test._testMethodName)
        super(DjangoNoseTextTestResult, self).addFailure(test, err)

    def addSuccess(self, test):
        """
        Custom add success
        """
        super(DjangoNoseTextTestResult, self).addSuccess(test)

    def printSummary(self, start, stop):
        """
        Custom printSummary to close all browsers when tests finish
        """
        super(DjangoNoseTextTestResult, self).printSummary(start, stop)
        BaseLiveTestCase.close_browsers()


class DjangoNoseTextTestRunner(TextTestRunner):
    """
    Custom class to modify result class
    """
    resultclass = DjangoNoseTextTestResult

    def _makeResult(self):
        return self.resultclass(self.stream,
                                self.descriptions,
                                self.verbosity,
                                self.config)


class NoseTestProgram(TestProgram):
    """
    Custom class to modify testRunner property
    """
    def runTests(self):
        if isinstance(self.testRunner, type):
            self.testRunner = self.testRunner(stream=self.config.stream,
                                              verbosity=self.config.verbosity,
                                              config=self.config)
        return super(NoseTestProgram, self).runTests()


class DjangoNoseTestSuiteRunner(django_nose.NoseTestSuiteRunner):
    """
    Custom class to modify testRunner property
    """
    test_runner = DjangoNoseTextTestRunner
    test_program = NoseTestProgram

    def run_suite(self, nose_argv):
        """Run the test suite."""
        result_plugin = ResultPlugin()
        plugins_to_add = [DjangoSetUpPlugin(self),
                          result_plugin,
                          TestReorderer()]

        for plugin in _get_plugins_from_settings():
            plugins_to_add.append(plugin)
        try:
            django.setup()
        except AttributeError:
            # Setup isn't necessary in Django < 1.7
            pass

        self.test_program(argv=nose_argv, exit=False, addplugins=plugins_to_add, testRunner=DjangoNoseTextTestRunner)
        return result_plugin.result
