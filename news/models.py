from django.db import models

from accounts.models import User


EMOTIONS = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
)


class Category(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Article(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    quick_view_image = models.ImageField(upload_to='news/article', blank=True, null=True)

    def __str__(self):
        return self.title

    def emotions(self):
        emotions_dict = {x[0]: 0 for x in EMOTIONS}
        emotions = self.emotion_set.all()
        emotions_dict.update({x.emotion: x.total for x in emotions})
        return emotions_dict

    def get_user_emotion(self, user):
        try:
            return self.useremotion_set.get(user=user).emotion
        except UserEmotion.DoesNotExist:
            return 0


class Message(models.Model):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(User)
    to_user = models.ForeignKey(User, related_name='to_users')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_from_author(self):
        return self.user == self.article.user


class Emotion(models.Model):
    article = models.ForeignKey(Article)
    emotion = models.IntegerField(choices=EMOTIONS)
    total = models.IntegerField(default=0)


class UserEmotion(models.Model):
    article = models.ForeignKey(Article)
    user = models.ForeignKey(User)
    emotion = models.IntegerField(choices=EMOTIONS)

    def delete(self, using=None, keep_parents=False):
        emotion = Emotion.objects.get(article=self.article, emotion=self.emotion)
        emotion.total -= 1
        emotion.save()

        super(UserEmotion, self).delete(using, keep_parents)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.id:
            # cancel update
            return
        emotion, created = Emotion.objects.get_or_create(article=self.article,
                                                         emotion=self.emotion,
                                                         defaults={'total': 1})
        if not created:
            emotion.total += 1
            emotion.save()
        super(UserEmotion, self).save(force_insert, force_update, using, update_fields)
