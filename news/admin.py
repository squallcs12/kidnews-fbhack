from functools import update_wrapper

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

from news import models
from news.tasks import send_message


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'user', 'to_user', 'content')

    def save_model(self, request, obj, form, change):
        super(MessageAdmin, self).save_model(request, obj, form, change)
        send_message.delay(obj.to_user.id, obj.article.id, obj.content)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'messages')

    def messages(self, obj):
        return '<a href="{}">Messages</a>'.format(reverse('admin:news_article_messages', args=(obj.id,)))
    messages.allow_tags = True

    def messages_view(self, request, object_id):
        model = self.model
        opts = model._meta

        add = False

        obj = self.get_object(request, unquote(object_id), 'id')

        ModelForm = self.get_form(request, obj)

        context = dict(self.admin_site.each_context(request),
                       title=(_('Add %s') if add else _('Change %s')) % force_text(opts.verbose_name),
                       object_id=object_id,
                       original=obj,
                       preserved_filters=self.get_preserved_filters(request),
                       )
        template = 'admin/news/messages.html'
        return TemplateResponse(request, template, context)

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = super(ArticleAdmin, self).get_urls()
        urlpatterns = [
            url(r'^(.+)/messages/$', wrap(self.messages_view), name='%s_%s_messages' % info),
        ] + urlpatterns

        return urlpatterns


admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.Article, ArticleAdmin)
