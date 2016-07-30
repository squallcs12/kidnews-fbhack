import hashlib
import hmac
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accountkit.models import Account
from fbmessages.models import FacebookUser
from fbmessages.services.message_service import MessageService

logger = logging.getLogger(__name__)

USER_PRESS_LOGIN = 'USER_PRESS_LOGIN'
message_service = MessageService()


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

        user = Account.objects.get(key=authorization_code).user
        if status == 'linked':
            FacebookUser.objects.create(user=user, facebook_id=sender_id)
        elif status == 'unlinked':
            fb_user = FacebookUser.objects.get(facebook_id=sender_id)
            fb_user.delete()

    def handle_postback(self, message):
        sender_id = self.get_sender_id(message)
        payload = message['postback']['payload']
        if payload == USER_PRESS_LOGIN:
            message_service.send_login_button(sender_id, self.build_absolute_uri(reverse('accountkit:login')))

    def build_absolute_uri(self, page):
        if getattr(self, 'request', None):
            return self.request.build_absolute_uri(page)
        return 'http://localhost:8000' + page

    def handle_received_message(self, message):
        """
        @param message:
        @return:
        """
        sender_id = self.get_sender_id(message)
        if not self.sender_is_first_time(sender_id):
            message_service.send_text_message(sender_id, message['message']['text'])

    def sender_is_first_time(self, sender_id):
        try:
            fbuser = FacebookUser.objects.get(pk=sender_id)
        except FacebookUser.DoesNotExist:
            message_service.send_login_options(sender_id)
            return True

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
