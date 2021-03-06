import logging

import requests
from django.conf import settings
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

USER_PRESS_LOGIN = 'USER_PRESS_LOGIN'


class MessageService:
    def send_message(self, recipient_id, message):
        message_data = {
            'recipient': {
                'id': recipient_id,
            },
            'message': message,
        }
        logger.warning(message_data)

        self.call_send_api(message_data)

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

            logger.info(_("Successfully sent generic message with "
                          "id {} to recipient {}").format(message_id, recipient_id))
        else:
            logger.warning(_("Unable to send message."))
            logger.warning(response.content)

    def send_login_options(self, recipient_id):
        self.send_message(recipient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": _("Please login to continue."),
                    "buttons": [
                        {
                            "type": "postback",
                            "title": _("Login"),
                            "payload": USER_PRESS_LOGIN,
                        },
                        {
                            "type": "postback",
                            "title": _("Not now"),
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

    def send_login_button(self, recepient_id, url):
        self.send_message(recepient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": _("Please press bellow button to login"),
                        "buttons": [{
                            "type": "account_link",
                            "url": url,
                        }],
                    }]
                }
            }
        })

    def send_notification_settings_message(self, recepient_id):
        self.send_message(recepient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": _("Mỗi ngày bạn sẽ được thông báo tin mới. Bạn muốn được thông báo tin mới "
                              "vào thời gian nào?"),
                    "buttons": [
                        {
                            "type": "postback",
                            "title": _("7h sáng"),
                            "payload": 'NOTIFICATION_07',
                        },
                        {
                            "type": "postback",
                            "title": _("12h trưa"),
                            "payload": 'NOTIFICATION_12',
                        },
                        {
                            "type": "postback",
                            "title": _("3h chiều"),
                            "payload": 'NOTIFICATION_15',
                        },
                    ]
                }
            }
        })

    def send_like_confirm_message(self, recepient_id, message):
        self.send_message(recepient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message,
                    "buttons": [
                        {
                            "type": "postback",
                            "title": _("Thích"),
                            "payload": 'LIKECONFIRM_LIKE',
                        },
                        {
                            "type": "postback",
                            "title": _("Không thích"),
                            "payload": 'LIKECONFIRM_NOTLIKE',
                        },
                    ]
                }
            }
        })
