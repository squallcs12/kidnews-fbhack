from django.contrib import admin

from accountkit import models


class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'data')


admin.site.register(models.Account, AccountAdmin)
