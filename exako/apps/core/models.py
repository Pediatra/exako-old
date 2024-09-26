from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.conf import settings


class UserBase(models.Model):
    """
    Este modelo é utilzado para definir um criador de um objeto que é definido automáticamente
    através de um middleware.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
        editable=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from exako.apps.core.middleware import get_current_user

        if not self.user:
            self.user = get_current_user()
        super().save(*args, **kwargs)

    save.alters_data = True


class CustomManager(models.Manager):
    def create(self, *args, **kwargs):
        fk_fields = [
            field
            for field in self.model._meta.get_fields()
            if isinstance(field, (models.ForeignKey, models.OneToOneField))
        ]
        for field in fk_fields:
            obj_id = kwargs.get(field.name)
            if isinstance(obj_id, int):
                obj = get_object_or_404(field.related_model, id=obj_id)
                kwargs[field.name] = obj
        return super().create(*args, **kwargs)
