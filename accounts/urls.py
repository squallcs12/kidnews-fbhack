from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from accounts.views.edit_profile_view import EditProfileView
from accounts.views.kid_viewset import KidViewSet
from accounts.views.profile_view import ProfileView

router = SimpleRouter()
router.register('kids', KidViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^profile', ProfileView.as_view(editable=True), name='profile'),
    url(r'^edit_profile', EditProfileView.as_view(), name='edit_profile'),
]
