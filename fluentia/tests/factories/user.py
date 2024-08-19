import factory
from factory import fuzzy

from fluentia.apps.term.constants import Language
from fluentia.apps.user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.Faker('password')
    native_language = fuzzy.FuzzyChoice(Language)
    is_superuser = False

    class Meta:
        model = User
