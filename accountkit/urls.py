from django.conf.urls import url

from accountkit.views.authenticate_view import AuthenticateView

urlpatterns = [
    url(r'^$', AuthenticateView.as_view(), name='authenticate'),
]
