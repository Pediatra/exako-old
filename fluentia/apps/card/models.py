from django.db import models

from fluentia.apps.term.constants import Language
from fluentia.apps.term.models import Term
from fluentia.apps.user.models import User


class CardSet(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    last_review = models.DateField()
    language = models.CharField(
        max_length=50,
        choices=Language.choices,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'card_set'


class Card(models.Model):
    note = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    cardset = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
