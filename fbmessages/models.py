from django.db import models

from accounts.models import User


class FacebookUser(models.Model):
    user = models.OneToOneField(User, null=True)
    facebook_id = models.IntegerField(primary_key=True)

