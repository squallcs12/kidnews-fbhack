from django.db import models

from accounts.models import User

NOTIFICATION_TIMES = (
    (7, '7AM'),
    (12, '12PM'),
    (15, '3PM'),
)


class FacebookUser(models.Model):
    user = models.OneToOneField(User, null=True)
    facebook_id = models.CharField(max_length=40, primary_key=True)
    notification_time = models.IntegerField(default=7, choices=NOTIFICATION_TIMES)
