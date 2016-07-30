from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from accounts.views.login_required_mixin import LoginRequiredMixin


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    editable = False

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update({
            'editable': self.editable,
        })

        return context
