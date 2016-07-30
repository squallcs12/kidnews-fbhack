from django.conf import settings
from pusher.pusher import Pusher

from root.celery import app

pusher = Pusher(app_id=settings.PUSHER_APP_ID, key=settings.PUSHER_APP_KEY, secret=settings.PUSHER_APP_SECRET)


@app.task
def send_message(user_id, article_id, message):
    channels = 'channel_article_{article_id}_{user_id}'.format(article_id=article_id, user_id=user_id)
    print(channels)
    pusher.trigger(channels,
                   'new_message',
                   {
                       'content': message,
                   })
