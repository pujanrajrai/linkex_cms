from django.db import models
from simple_history.models import HistoricalRecords

from uuid import uuid4

from base.mixins import CaseSensitiveFieldsMixin
from base.utils import process_string_fields


class NonDeleted(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model, CaseSensitiveFieldsMixin):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    objects = NonDeleted()

    everything = models.Manager()

    class Meta:
        ordering = ['-created_at']
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        process_string_fields(self, exclude_fields=self.CASE_SENSITIVE_FIELDS)
        super().save(*args, **kwargs) 
