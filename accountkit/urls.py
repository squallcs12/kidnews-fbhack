from django.conf.urls import url

from accountkit.views.authenticate_view import AuthenticateView
from accountkit.views.login_view import LoginView

urlpatterns = [
    url(r'^authenticate$', AuthenticateView.as_view(), name='authenticate'),
    url(r'^login', LoginView.as_view(), name='login'),
]
