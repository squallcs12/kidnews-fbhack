from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from pusher.pusher import Pusher

from accounts.models import User
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
def notify_new_article_on_fbmessage(article_id, base_url, facebook_id=None, **user_filter):
    print(base_url)
    article = Article.objects.get(pk=article_id)
    if facebook_id:
        fb_user_ids = [facebook_id]
    else:
        fb_user_ids = FacebookUser.objects.all().filter(**user_filter).values_list('facebook_id', flat=True)
    message_service = MessageService()
    for fb_user_id in fb_user_ids:
        message_service.send_text_message(fb_user_id, 'Tin tức mới nhất cho con ban là "{}"'.format(article.title))
        image_url = article.quick_view_image.url
        if not image_url.startswith("http"):
            image_url = base_url + image_url
        if article.quick_view_image:
            message_service.send_message(fb_user_id, {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": image_url
                    }
                },
            })
        if article.additional_fb_message:
            message_service.send_text_message(fb_user_id, article.additional_fb_message)


@app.task
def notify_new_chat_on_fbmessage(article_id, user_id):
    try:
        facebook_user = FacebookUser.objects.get(user=user_id)
    except FacebookUser.DoesNotExist:
        return
    else:
        article = Article.objects.get(pk=article_id)
        message_service = MessageService()
        message = ("Bé vừa gửi một câu hỏi cho biên tập của KIDNEWS. Hình như bé rất thích tin \"{}\"vừa đọc đó nha! "
                   "^^ Đúng không bạn?".format(article.title))
        message_service.send_like_confirm_message(facebook_user.facebook_id, message)


@app.task
def notify_new_art_on_fbmessage(article_id, user_id):
    try:
        facebook_user = FacebookUser.objects.get(user=user_id)
    except FacebookUser.DoesNotExist:
        return
    else:
        article = Article.objects.get(pk=article_id)
        message_service = MessageService()
        message = ("Bé vừa hoàn thành một bức tranh từ nội dung \"{}\". "
                   "Ghé qua coi đi nào! Chắc bạn sẽ thích đó.".format(article.title))
        message_service.send_like_confirm_message(facebook_user.facebook_id, message)


@app.task
def daily_notification():
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    article = Article.objects.filter(created_at__gte=yesterday).first()
    notify_new_article_on_fbmessage(article.id, settings.BASE_URL, notification_time=now.hour)
