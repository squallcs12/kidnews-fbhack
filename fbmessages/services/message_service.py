import logging

import requests
from django.conf import settings

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

            logger.info("Successfully sent generic message with "
                        "id {} to recipient {}".format(message_id, recipient_id))
        else:
            logger.warning("Unable to send message.")
            logger.warning(response.content)

    def send_login_options(self, recipient_id):
        self.send_message(recipient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Please login to continue.",
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

    def send_login_button(self, recepient_id, url):
        self.send_message(recepient_id, {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "Please press bellow button to login",
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
                    "text": "Mỗi ngày bạn sẽ được thông báo tin mới. Bạn muốn được thông báo tin mới vào thời gian nào?",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "7h sang",
                            "payload": 'NOTIFICATION_07',
                        },
                        {
                            "type": "postback",
                            "title": "12h trua",
                            "payload": 'NOTIFICATION_12',
                        },
                        {
                            "type": "postback",
                            "title": "3h chieu",
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
                            "title": "Thich",
                            "payload": 'LIKECONFIRM_LIKE',
                        },
                        {
                            "type": "postback",
                            "title": "Khong thich",
                            "payload": 'LIKECONFIRM_NOTLIKE',
                        },
                    ]
                }
            }
        })
