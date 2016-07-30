from django.db import models

from accounts.models import User


class Article(models.Model):
    author = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(User)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
