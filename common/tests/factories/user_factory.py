import factory
from django.contrib.auth import get_user_model
from factory.helpers import lazy_attribute

from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: u'User{0}'.format(n))
    password = 'password'
    email = lazy_attribute(lambda a: fake.email())
    first_name = lazy_attribute(lambda a: fake.first_name())
    last_name = lazy_attribute(lambda a: fake.last_name())

    is_superuser = True
    is_staff = True
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)

        user.raw_password = password
        user.set_password(password)
        if create:
            user.save()

        return user

    class Meta:
        model = get_user_model()
