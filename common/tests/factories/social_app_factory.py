from allauth.socialaccount.models import SocialAccount
import factory

from common.tests.core import fake
from common.tests.factories.user_factory import UserFactory


class SocialAccountFactory(factory.DjangoModelFactory):

    user = factory.SubFactory(UserFactory)
    provider = 'google'
    uid = factory.Sequence(lambda n: fake.word())

    class Meta:
        model = SocialAccount
