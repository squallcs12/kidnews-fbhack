from django.conf.urls import url

from fbmessages.views.webhook_view import WebhookView


urlpatterns = [
    url(r'^webhook', WebhookView.as_view(), name='fbwebhook'),
]
