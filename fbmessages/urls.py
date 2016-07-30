from django.conf.urls import url

from fbmessages.views.authenticate_view import AuthenticateView
from fbmessages.views.webhook_view import WebhookView


urlpatterns = [
    url(r'^webhook', WebhookView.as_view(), name='fbwebhook'),
    url(r'^authenticate', AuthenticateView.as_view(), name='authenticate'),
]
