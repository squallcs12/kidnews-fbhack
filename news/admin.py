from django.contrib import admin

from news import models


admin.site.register(models.Message)
admin.site.register(models.Article)
