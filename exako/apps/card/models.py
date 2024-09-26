from django.db import models

from exako.apps.core.models import UserBase
from exako.apps.term.constants import Language
from exako.apps.term.models import Term


class CardSet(UserBase):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_review = models.DateTimeField(auto_now=True)
    pinned = models.BooleanField(default=False)
    language = models.CharField(
        max_length=50,
        choices=Language.choices,
        null=True,
        blank=True,
    )

    def get_language_label(self):
        return Language(str(self.language)).label

    class Meta:
        db_table = 'card_set'


class Card(models.Model):
    note = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    last_review = models.DateField(auto_now=True)
    cardset = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
