from django.db import models
from django.shortcuts import get_object_or_404


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
