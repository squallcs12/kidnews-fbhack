from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Kid(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=80)
    birthyear = models.IntegerField()
    picture = models.ImageField(upload_to='accounts/kids', null=True, blank=True)
