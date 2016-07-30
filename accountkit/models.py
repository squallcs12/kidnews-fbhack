import binascii
import os

from django.db import models

from accounts.models import User


class Account(models.Model):
    user = models.OneToOneField(User)
    account_id = models.CharField(max_length=40)
    data = models.TextField()
    key = models.CharField(max_length=40, primary_key=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Account, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()


