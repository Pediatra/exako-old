import factory

from fluentia.apps.card.models import Card, CardSet
from fluentia.apps.term.constants import Language
from fluentia.tests.factories.term import TermFactory
from fluentia.tests.factories.user import UserFactory


class CardSetFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    description = factory.Faker('sentence')
    language = factory.fuzzy.FuzzyChoice(Language)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = CardSet


class CardFactory(factory.django.DjangoModelFactory):
    cardset = factory.SubFactory(CardSetFactory)
    note = factory.Faker('sentence')
    term = factory.SubFactory(TermFactory)

    class Meta:
        model = Card
