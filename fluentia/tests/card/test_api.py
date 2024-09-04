import pytest
from django.urls import reverse_lazy

from fluentia.apps.card.api.schema import CardSchemaView, CardSetSchemaView
from fluentia.apps.card.models import Card
from fluentia.apps.core.query import set_url_params
from fluentia.apps.term.constants import Language
from fluentia.tests.factories.card import CardFactory, CardSetFactory
from fluentia.tests.factories.term import TermFactory

pytestmark = pytest.mark.django_db


class TestCardSet:
    create_cardset_route = reverse_lazy('api-1.0.0:create_cardset')

    def list_cardset_route(self, name=None):
        url = str(reverse_lazy('api-1.0.0:list_cardset'))
        return set_url_params(url, name=name)

    def get_cardset_route(self, cardset_id):
        return reverse_lazy('api-1.0.0:get_cardset', kwargs={'cardset_id': cardset_id})

    def update_cardset_route(self, cardset_id):
        return reverse_lazy(
            'api-1.0.0:update_cardset', kwargs={'cardset_id': cardset_id}
        )

    def delete_cardset_route(self, cardset_id):
        return reverse_lazy(
            'api-1.0.0:delete_cardset', kwargs={'cardset_id': cardset_id}
        )

    def test_create_cardset(self, client, generate_payload, user, token_header):
        payload = generate_payload(CardSetFactory)
        payload['user_id'] = user.id

        response = client.post(
            self.create_cardset_route,
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 201
        assert CardSetSchemaView(**response.json()) == CardSetSchemaView(
            id=response.json()['id'],
            created_at=response.json()['created_at'],
            last_review=response.json()['last_review'],
            **payload,
        )

    def test_create_cardset_user_not_authenticated(
        self, client, user, generate_payload
    ):
        payload = generate_payload(CardSetFactory)
        payload['user_id'] = user.id

        response = client.post(
            self.create_cardset_route,
            payload,
            content_type='application/json',
        )

        assert response.status_code == 401

    def test_list_cardset(self, client, user, token_header):
        cardsets = CardSetFactory.create_batch(size=5, user=user)
        CardSetFactory.create_batch(size=10)

        response = client.get(self.list_cardset_route(), headers=token_header)

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert [CardSetSchemaView(**cardset) for cardset in response.json()] == [
            CardSetSchemaView.from_orm(cardset) for cardset in cardsets
        ]

    def test_list_cardset_filter_name(self, client, user, token_header):
        cardsets = CardSetFactory.create_batch(
            size=5, user=user, name='ãQübérmäßíg âçãoQã'
        )
        CardSetFactory.create_batch(size=5, user=user)
        CardSetFactory.create_batch(size=10)

        response = client.get(
            self.list_cardset_route(name='aqubermassig acaoqa'), headers=token_header
        )

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert [CardSetSchemaView(**cardset) for cardset in response.json()] == [
            CardSetSchemaView.from_orm(cardset) for cardset in cardsets
        ]

    def test_list_cardset_user_is_not_authenticated(self, client):
        CardSetFactory.create_batch(size=10)

        response = client.get(self.list_cardset_route())

        assert response.status_code == 401

    def test_list_cardset_dont_belongs_to_user(self, client, token_header):
        CardSetFactory.create_batch(size=5)

        response = client.get(self.list_cardset_route(), headers=token_header)

        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_cardset(self, client, user, token_header):
        cardset = CardSetFactory(user=user)

        response = client.get(self.get_cardset_route(cardset.id), headers=token_header)

        assert response.status_code == 200
        assert CardSetSchemaView(**response.json()) == CardSetSchemaView.from_orm(
            cardset
        )

    def test_get_cardset_user_is_not_authenticated(self, client):
        cardset = CardSetFactory()

        response = client.get(self.get_cardset_route(cardset.id))

        assert response.status_code == 401

    def test_get_cardset_dont_belongs_to_user(self, client, token_header):
        cardset = CardSetFactory()

        response = client.get(self.get_cardset_route(cardset.id), headers=token_header)

        assert response.status_code == 404

    def test_get_cardset_does_not_exists(self, client, token_header):
        response = client.get(self.get_cardset_route(123), headers=token_header)

        assert response.status_code == 404

    def test_update_cardset(self, client, generate_payload, user, token_header):
        cardset = CardSetFactory(user=user)
        payload = generate_payload(CardSetFactory, include={'name', 'description'})

        response = client.patch(
            self.update_cardset_route(cardset.id),
            payload,
            content_type='application/json',
            headers=token_header,
        )
        cardset.refresh_from_db()

        assert response.status_code == 200
        assert cardset.name == payload['name']
        assert cardset.description == payload['description']
        assert cardset.last_review is not None

    def test_update_cardset_user_is_not_authenticated(self, client, generate_payload):
        cardset = CardSetFactory()
        payload = generate_payload(CardSetFactory, include={'name', 'description'})

        response = client.patch(
            self.update_cardset_route(cardset.id),
            payload,
            content_type='application/json',
        )

        assert response.status_code == 401

    def test_update_cardset_dont_belongs_to_user(
        self, client, generate_payload, token_header
    ):
        cardset = CardSetFactory()
        payload = generate_payload(CardSetFactory, include={'name', 'description'})

        response = client.patch(
            self.update_cardset_route(cardset.id),
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_update_cardset_does_not_exists(
        self, client, generate_payload, token_header
    ):
        payload = generate_payload(CardSetFactory, include={'name', 'description'})

        response = client.patch(
            self.update_cardset_route(123),
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_delete_cardset(self, client, user, token_header):
        cardset = CardSetFactory(user=user)

        response = client.delete(
            self.delete_cardset_route(cardset.id), headers=token_header
        )

        assert response.status_code == 204

    def test_delete_cardset_user_is_not_authenticated(self, client):
        cardset = CardSetFactory()

        response = client.delete(self.delete_cardset_route(cardset.id))

        assert response.status_code == 401

    def test_delete_cardset_dont_belongs_to_user(self, client, token_header):
        cardset = CardSetFactory()

        response = client.delete(
            self.delete_cardset_route(cardset.id), headers=token_header
        )

        assert response.status_code == 404
        assert cardset is not None

    def test_delete_cardset_does_not_exists(self, client, token_header):
        response = client.delete(self.delete_cardset_route(123), headers=token_header)

        assert response.status_code == 404


class TestCard:
    create_card_route = reverse_lazy('api-1.0.0:create_card')

    def get_card_route(self, card_id):
        return reverse_lazy('api-1.0.0:get_card', kwargs={'card_id': card_id})

    def list_cards_route(self, cardset_id, expression=None, note=None):
        url = str(
            reverse_lazy('api-1.0.0:list_cards', kwargs={'cardset_id': cardset_id})
        )
        return set_url_params(url, expression=expression, note=note)

    def update_card_route(self, card_id):
        return reverse_lazy('api-1.0.0:update_card', kwargs={'card_id': card_id})

    def delete_card_route(self, card_id):
        return reverse_lazy('api-1.0.0:delete_card', kwargs={'card_id': card_id})

    def test_create_card(self, client, user, generate_payload, token_header):
        term = TermFactory()
        cardset = CardSetFactory(user=user)
        payload = generate_payload(
            CardFactory,
            cardset=cardset,
            term=term,
        )
        payload['cardset_id'] = cardset.id
        payload['expression'] = term.expression
        payload['origin_language'] = term.origin_language

        response = client.post(
            self.create_card_route,
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 201
        assert CardSchemaView.from_orm(Card.objects.get(id=response.json()['id']))

    def test_create_card_user_is_not_authenticated(self, client, generate_payload):
        term = TermFactory()
        cardset = CardSetFactory()
        payload = generate_payload(
            CardFactory,
            cardset=cardset,
            term=term,
        )
        payload['cardset_id'] = cardset.id
        payload['expression'] = term.expression
        payload['origin_language'] = term.origin_language

        response = client.post(
            self.create_card_route,
            payload,
            content_type='application/json',
        )

        assert response.status_code == 401

    def test_create_card_term_does_not_exists(
        self, client, generate_payload, user, token_header
    ):
        cardset = CardSetFactory(user=user)
        payload = generate_payload(
            CardFactory,
            cardset=cardset,
        )
        payload['cardset_id'] = cardset.id
        payload['expression'] = 'not'
        payload['origin_language'] = Language.PORTUGUESE

        response = client.post(
            self.create_card_route,
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_create_card_cardset_does_not_exists(
        self, client, generate_payload, token_header
    ):
        term = TermFactory()
        payload = generate_payload(
            CardFactory,
            term=term,
        )
        payload['cardset_id'] = 123
        payload['expression'] = term.expression
        payload['origin_language'] = term.origin_language

        response = client.post(
            self.create_card_route,
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_create_card_cardset_dont_belongs_to_user(
        self, client, generate_payload, token_header
    ):
        term = TermFactory()
        cardset = CardSetFactory()
        payload = generate_payload(
            CardFactory,
            cardset=cardset,
            term=term,
        )
        payload['cardset_id'] = cardset.id
        payload['expression'] = term.expression
        payload['origin_language'] = term.origin_language

        response = client.post(
            self.create_card_route,
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_get_card(self, client, user, token_header):
        cardset = CardSetFactory(user=user)
        card = CardFactory(cardset=cardset)

        response = client.get(self.get_card_route(card.id), headers=token_header)

        assert response.status_code == 200
        assert CardSchemaView.from_orm(card)

    def test_get_card_user_is_not_authenticated(self, client):
        card = CardFactory()

        response = client.get(self.get_card_route(card.id))

        assert response.status_code == 401

    def test_get_card_does_not_exists(self, client, token_header):
        response = client.get(self.get_card_route(123), headers=token_header)

        assert response.status_code == 404

    def test_get_card_cardset_dont_belongs_to_user(self, client, token_header):
        card = CardFactory()

        response = client.get(self.get_card_route(card.id), headers=token_header)

        assert response.status_code == 404

    def test_list_cards(self, client, user, token_header):
        cardset = CardSetFactory(user=user)
        cards = CardFactory.create_batch(cardset=cardset, size=5)
        CardFactory.create_batch(size=5)

        response = client.get(self.list_cards_route(cardset.id), headers=token_header)

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert len([CardSchemaView.from_orm(card) for card in cards]) == 5

    def test_list_cards_filter_expression(self, client, user, token_header):
        cardset = CardSetFactory(user=user)
        CardFactory.create_batch(cardset=cardset, size=5)
        term = TermFactory(expression='übérmäßíg âção')
        cards = CardFactory.create_batch(term=term, cardset=cardset, size=5)
        CardFactory.create_batch(size=5)

        response = client.get(
            self.list_cards_route(cardset.id, expression='ubermassig acao'),
            headers=token_header,
        )

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert len([CardSchemaView.from_orm(card) for card in cards]) == 5

    def test_list_cards_filter_note(self, client, user, token_header):
        cardset = CardSetFactory(user=user)
        CardFactory.create_batch(cardset=cardset, size=5)
        cards = CardFactory.create_batch(note='übérmäßíg âção', cardset=cardset, size=5)
        CardFactory.create_batch(size=5)

        response = client.get(
            self.list_cards_route(cardset.id, note='ubermassig acao'),
            headers=token_header,
        )

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert len([CardSchemaView.from_orm(card) for card in cards]) == 5

    def test_list_cards_user_is_not_authenticated(self, client):
        cardset = CardSetFactory()
        CardFactory.create_batch(size=15)

        response = client.get(self.list_cards_route(cardset.id))

        assert response.status_code == 401

    def test_list_cards_cardset_does_not_exists(self, client, token_header):
        response = client.get(self.list_cards_route(123), headers=token_header)

        assert response.status_code == 404

    def test_list_cards_cardset_dont_belongs_to_user(self, client, token_header):
        cardset = CardSetFactory()
        CardFactory.create_batch(cardset=cardset, size=15)

        response = client.get(self.list_cards_route(cardset.id), headers=token_header)

        assert response.status_code == 404

    def test_update_card(self, client, user, token_header):
        cardset = CardSetFactory(user=user)
        card = CardFactory(cardset=cardset)
        payload = {'note': 'test note'}

        response = client.patch(
            self.update_card_route(card.id),
            payload,
            content_type='application/json',
            headers=token_header,
        )
        card.refresh_from_db()

        assert response.status_code == 200
        assert card.note == payload['note']

    def test_update_card_user_is_not_authenticated(self, client):
        cardset = CardSetFactory()
        card = CardFactory(cardset=cardset)
        payload = {'note': 'test note'}

        response = client.patch(
            self.update_card_route(card.id),
            payload,
            content_type='application/json',
        )

        assert response.status_code == 401

    def test_update_card_does_not_exists(self, client, token_header):
        payload = {'note': 'test note'}

        response = client.patch(
            self.update_card_route(123),
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_update_card_cardset_dont_belongs_to_user(self, client, token_header):
        cardset = CardSetFactory()
        card = CardFactory(cardset=cardset)
        payload = {'note': 'test note'}

        response = client.patch(
            self.update_card_route(card.id),
            payload,
            content_type='application/json',
            headers=token_header,
        )

        assert response.status_code == 404

    def test_delete_card(self, client, user, token_header):
        cardset = CardSetFactory(user=user)
        card = CardFactory(cardset=cardset)

        response = client.delete(self.delete_card_route(card.id), headers=token_header)

        assert response.status_code == 204

    def test_delete_card_user_is_not_authenticated(self, client):
        cardset = CardSetFactory()
        card = CardFactory(cardset=cardset)

        response = client.delete(self.delete_card_route(card.id))

        assert response.status_code == 401

    def test_delete_card_does_not_exists(self, client, token_header):
        response = client.delete(self.delete_card_route(123), headers=token_header)

        assert response.status_code == 404

    def test_delete_card_cardset_dont_belongs_to_user(self, client, token_header):
        cardset = CardSetFactory()
        card = CardFactory(cardset=cardset)

        response = client.delete(self.delete_card_route(card.id), headers=token_header)

        assert response.status_code == 404
