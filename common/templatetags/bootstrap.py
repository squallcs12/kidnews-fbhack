from django import template
from django.forms.fields import DateField, DateTimeField

register = template.Library()


@register.inclusion_tag('general/form_requirement.html')
def form_requirements(form):
    """
    Add form required js/css base on form elements
    @param form: Form need to be displayed
    @type form: django.forms.Form
    @return: dict
    """
    context = {}
    for bound_field in form:
        bound_field.field.widget.attrs['class'] = 'form-control'
        if isinstance(bound_field.field, (DateField, DateTimeField)):
            context['datetimepicker'] = True
            if isinstance(bound_field.field, DateField):
                bound_field.field.datepicker = True
            else:
                bound_field.field.datetimepicker = True
    return context


@register.inclusion_tag('_notification_message.html')
def render_message(message):
    """
    Render message to html
    @param message: message need to be displayed
    @type message: django.contrib.messages.storage.base.Message
    @return:
    """
    tags = message.tags.replace('error', 'danger')
    tags = ' '.join('alert-{tag}'.format(tag=x) for x in tags.split(' '))
    message.class_tags = tags
    return {'message': message}
