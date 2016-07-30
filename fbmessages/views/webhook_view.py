import hashlib
import hmac
import logging

import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accountkit.models import Account
from fbmessages.models import FacebookUser

logger = logging.getLogger(__name__)

USER_PRESS_LOGIN = 'USER_PRESS_LOGIN'


class WebhookView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        """
        @param request:
        @type request: django.http.request.HttpRequest
        @return:
        """
        if request.GET.get('hub.mode') == 'subscribe':
            if request.GET.get('hub.verify_token') == settings.PAGE_MSG_VALIDATION_TOKEN:
                return HttpResponse(request.GET.get('hub.challenge'))

        return HttpResponseForbidden()

    def handle_page(self, data):
        entries = data['entry']
        for entry in entries:
            self.handle_entry(entry)

    def handle_entry(self, entry):
        """
        @param entry:
        @return:
        """
        for message in entry['messaging']:
            self.handle_message(message)

    def handle_message(self, message):
        if message.get('message'):
            self.handle_received_message(message)
        if message.get('postback'):
            self.handle_postback(message)
        if message.get('account_linking'):
            self.handle_account_linking(message)

    def get_sender_id(self, message):
        return message['sender']['id']

    def handle_account_linking(self, message):
        sender_id = self.get_sender_id(message)
        account_linking = message['account_linking']
        status = account_linking['status']
        authorization_code = account_linking.get('authorization_code')

        user = Account.objects.get(key=authorization_code)
        if status == 'linked':
            FacebookUser.objects.create(user=user, facebook_id=sender_id)
        elif status == 'unlinked':
            fb_user = FacebookUser.objects.get(facebook_id=sender_id)
            fb_user.delete()

    def handle_postback(self, message):
        sender_id = self.get_sender_id(message)
        payload = message['postback']['payload']
        if payload == USER_PRESS_LOGIN:
            self.send_login_button(sender_id)

    def build_absolute_uri(self, page):
        if getattr(self, 'request', None):
            self.request.build_absolute_uri(page)
        return 'http://localhost:8000' + page

    def send_login_button(self, recepient_id):
        self.send_message(recepient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Please press bellow button to login",
                        "buttons": [{
                            "type": "account_link",
                            "url": self.build_absolute_uri(reverse('accountkit:login')),
                        }],
                    }]
                }
            }
        })

    def handle_received_message(self, message):
        """
        @param message:
        @return:
        """
        sender_id = self.get_sender_id(message)
        if not self.sender_is_first_time(sender_id):
            self.send_text_message(sender_id, message['message']['text'])

    def sender_is_first_time(self, sender_id):
        try:
            fbuser = FacebookUser.objects.get(pk=sender_id)
        except FacebookUser.DoesNotExist:
            self.send_login_options(sender_id)
            return True

    def send_message(self, recipient_id, message):
        message_data = {
            'recipient': {
                'id': recipient_id
            },
            'message': message,
        }

        self.call_send_api(message_data)

    def send_login_options(self, recipient_id):
        self.send_message(recipient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "What do you want to do next?",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Login",
                            "payload": USER_PRESS_LOGIN,
                        },
                        {
                            "type": "postback",
                            "title": "Not now",
                            "payload": "USER_NOT_LOGIN",
                        }
                    ]
                }
            }
        })

    def send_text_message(self, recipient_id, message):
        self.send_message(recipient_id, {
            'text': message
        })

    @property
    def send_api_endpoint(self):
        return 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(settings.PAGE_MSG_ACCESS_TOKEN)

    def call_send_api(self, data):
        """
        @param data:
        @return:
        """
        response = requests.post(self.send_api_endpoint, json=data)
        if response.status_code == 200:
            response_json = response.json()
            recipient_id = response_json['recipient_id']
            message_id = response_json['message_id']

            logger.info("Successfully sent generic message with "
                        "id {} to recipient {}".format(message_id, recipient_id))
        else:
            logger.warning("Unable to send message.")
            logger.warning(response.content)

    def is_from_facebook(self):
        signature = 'sha1=' + hmac.new(settings.ACCOUNT_KIT_APP_ID.encode('utf-8'),
                                       self.request.body,
                                       hashlib.sha1).hexdigest()
        if signature == self.request.META.get('HTTP_X_HUB_SIGNATURE'):
            return True
        logger.warning(self.request.META)
        logger.warning(signature)
        return True

    def post(self, request):
        """
        @param request:
        @return:
        """
        if self.is_from_facebook():
            logger.warning(request.data)
            obj = request.data.get('object', '')
            if obj == 'page':
                self.handle_page(request.data)
            return HttpResponse()
        return HttpResponseBadRequest()
