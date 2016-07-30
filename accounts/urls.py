from django.conf.urls import url

from accounts.views.edit_profile_view import EditProfileView
from accounts.views.profile_view import ProfileView


urlpatterns = [
    url(r'^profile', ProfileView.as_view(editable=True), name='profile'),
    url(r'^edit_profile', EditProfileView.as_view(), name='edit_profile'),
]
