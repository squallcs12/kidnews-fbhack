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
from news.models import Article
from news.tasks import notify_new_article_on_fbmessage

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
            article = Article.objects.all().order_by('id').first()
            if article:
                notify_new_article_on_fbmessage.delay(article.id,
                                                      self.request.build_absolute_uri('/'),
                                                      facebook_id=sender_id)
            message_service.send_notification_settings_message(sender_id)
        elif status == 'unlinked':
            fb_user = FacebookUser.objects.get(facebook_id=sender_id)
            fb_user.delete()

    def send_login_button(self, sender_id):
        message_service.send_login_button(sender_id, self.build_absolute_uri(reverse('accountkit:login')))

    def handle_postback(self, message):
        sender_id = self.get_sender_id(message)
        payload = message['postback']['payload']
        payload_parts = payload.split('_')
        if payload == USER_PRESS_LOGIN:
            self.send_login_button(sender_id)
        elif payload_parts[0] == 'NOTIFICATION':
            self.handle_postback_notification(sender_id, payload_parts)
        elif payload_parts[0] == 'LIKECONFIRM':
            self.handle_like_confirm(sender_id, payload_parts)

    def send_happy_message(self, sendder_id):
        message_service.send_text_message(sendder_id, ':)')
        message_service.send_text_message(sendder_id, 'Hi hi. Cam on ban nhieu')

    def send_sad_message(self, sendder_id):
        message_service.send_text_message(sendder_id, ':(')
        message_service.send_text_message(sendder_id, 'Minh rat tiec.')

    def handle_like_confirm(self, sendder_id, payload_parts):
        if payload_parts[1] == 'LIKE':
            self.send_happy_message(sendder_id)
        else:
            self.send_sad_message(sendder_id)

    def handle_postback_notification(self, sender_id, payload_parts):
        notification_time = payload_parts[1]
        try:
            facebook_user = FacebookUser.objects.get(facebook_id=sender_id)
            facebook_user.notification_time = notification_time
            facebook_user.save()
            message_service.send_message(sender_id, "Ok. {} nhe.".format(notification_time))
        except FacebookUser.DoesNotExist:
            self.send_login_button(sender_id)

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
        message_text = message['message']['text']
        if message_text == 'login':
            message_service.send_text_message(sender_id, message_text)
        elif message_text == 'notification':
            message_service.send_notification_settings_message(sender_id)

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
