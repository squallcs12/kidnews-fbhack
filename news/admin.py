from django.contrib import admin

from news import models
from news.tasks import send_message


class MessageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super(MessageAdmin, self).save_model(request, obj, form, change)
        send_message.delay(request.user.id, obj.article.id, obj.content)


admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.Article)
