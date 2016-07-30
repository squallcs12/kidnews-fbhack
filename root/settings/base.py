"""
Django settings for root project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.core.urlresolvers import reverse_lazy


default = {
    'DEBUG': (bool, True),
    'SECRET_KEY': (str, '#3pw2ogg-#q7r%abn2sy+zsaqnek2tp7g@ke+za46)#hb+pbka'),
    'ALLOWED_HOSTS': (str, '*'),
    'DATABASE_URL': (str, 'sqlite:///db.sqlite3'),
    'EMAIL_URL': (str, ''),
    'DEFAULT_FROM_EMAIL': (str, 'admin@example.com'),
    'AUTH_FACEBOOK_KEY': (str, ''),
    'AUTH_FACEBOOK_SECRET': (str, ''),
    'AUTH_GOOGLE_KEY': (str, ''),
    'AUTH_GOOGLE_SECRET': (str, ''),
    'AUTH_TWITTER_KEY': (str, ''),
    'AUTH_TWITTER_SECRET': (str, ''),
    'ACCOUNT_KIT_API_VERSION': (str, 'v1.0'),
    'ACCOUNT_KIT_APP_SECRET': (str, ''),
    'ACCOUNT_KIT_APP_ID': (str, ''),
    'AWS_ACCESS_KEY_ID': (str, ''),
    'AWS_SECRET_ACCESS_KEY': (str, ''),
    'AWS_STORAGE_BUCKET_NAME': (str, ''),
    'SITE_NAME': (str, 'Django'),
    'PAGE_MSG_VALIDATION_TOKEN': (str, 'PAGE_MSG_VALIDATION_TOKEN'),
    'PAGE_MSG_ACCESS_TOKEN': (str, 'PAGE_MSG_ACCESS_TOKEN'),
    'DEFAULT_FILE_STORAGE': (str, 'django.core.files.storage.FileSystemStorage'),
    'PUSHER_APP_ID': (str, ''),
    'PUSHER_APP_KEY': (str, ''),
    'PUSHER_APP_SECRET': (str, ''),
}

env = environ.Env(**default)
ENV = env  # so it will be copied to django.conf.settings
env.read_env('.env')

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root = environ.Path(__file__) - 3
BASE_DIR = root()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')
ALLOWED_HOSTS = ALLOWED_HOSTS.split(',') if ALLOWED_HOSTS else []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # The Django sites framework is required
    'django.contrib.sites',

    'django_extensions',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'djcelery_email',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'rest_framework_swagger',

    'accounts',
    'common',
    'accountkit',
    'news',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'root.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.site_name',
            ],
        },
    },
]

WSGI_APPLICATION = 'root.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': env.db()
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = 'static'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'

AUTH_USER_MODEL = 'accounts.User'

SITE_NAME = os.getenv('SITE_NAME', 'Django')
SITE_ID = 1

TEST_RUNNER = 'common.tests.core.DjangoNoseTestSuiteRunner'

LOGIN_URL = reverse_lazy('two_factor:login')
LOGIN_ERROR_URL = reverse_lazy('two_factor:login')
LOGIN_REDIRECT_URL = reverse_lazy('accounts:profile')

vars().update(env.email(backend='djcelery_email.backends.CeleryEmailBackend'))
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
PUSHER_APP_ID = env('PUSHER_APP_ID')
PUSHER_APP_KEY = env('PUSHER_APP_KEY')
PUSHER_APP_SECRET = env('PUSHER_APP_SECRET')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'accountkit.authentication.TokenAuthentication',
    )
}

AUTH_FACEBOOK_KEY = env('AUTH_FACEBOOK_KEY')
AUTH_FACEBOOK_SECRET = env('AUTH_FACEBOOK_SECRET')
ACCOUNT_KIT_API_VERSION = env('ACCOUNT_KIT_API_VERSION')
ACCOUNT_KIT_APP_SECRET = env('ACCOUNT_KIT_APP_SECRET')
ACCOUNT_KIT_APP_ID = env('ACCOUNT_KIT_APP_ID')
FACEBOOK_APP_ID = AUTH_FACEBOOK_KEY
