from django.conf import settings
from pusher.pusher import Pusher

from fbmessages.models import FacebookUser
from fbmessages.services.message_service import MessageService
from news.models import Article
from root.celery import app

pusher = Pusher(app_id=settings.PUSHER_APP_ID, key=settings.PUSHER_APP_KEY, secret=settings.PUSHER_APP_SECRET)


@app.task
def send_message(user_id, article_id, message):
    channels = 'channel_article_{article_id}_{user_id}'.format(article_id=article_id, user_id=user_id)
    pusher.trigger(channels,
                   'new_message',
                   {
                       'content': message,
                   })


@app.task
def notify_new_article_on_fbmessage(article_id, base_url):
    print(base_url)
    article = Article.objects.get(pk=article_id)
    fb_user_ids = FacebookUser.objects.all().values_list('facebook_id', flat=True)
    message_service = MessageService()
    for fb_user_id in fb_user_ids:
        message_service.send_text_message(fb_user_id, 'Ok. Tin tức mới nhất cho con ban là "{}"'.format(article.title))
        if article.quick_view_image:
            message_service.send_message(fb_user_id, {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": base_url + article.quick_view_image.url,
                    }
                },
            })
        if article.additional_fb_message:
            message_service.send_text_message(fb_user_id, article.additional_fb_message)
