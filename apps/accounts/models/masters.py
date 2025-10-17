from base.models import BaseModel
from django.db import models
from simple_history.models import HistoricalRecords


class Country(BaseModel):
    history = HistoricalRecords()
    name = models.CharField(max_length=30, unique=True)
    short_name = models.CharField(max_length=6)
    code = models.CharField(max_length=10)
    couriex_code = models.CharField(max_length=10, null=True, blank=True)
    priority = models.IntegerField(default=0, help_text="Priority for sorting")
    search_key = models.CharField(
        max_length=100, null=True, blank=True, help_text="Search key for filtering")

    class Meta:
        ordering = ['-priority']

    def __str__(self):
        return f"{self.short_name}-{self.name}"


class ZipCode(BaseModel):
    history = HistoricalRecords()
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="zip_codes")
    city = models.CharField(max_length=100, help_text="City name")
    state_county = models.CharField(
        max_length=100,
        help_text="State or County"
    )
    state_abbreviation = models.CharField(
        max_length=100, null=True, blank=True
    )
    postal_code = models.CharField(
        max_length=20, help_text="Postal/ZIP Code")

    def __str__(self):
        return f"{self.postal_code} - {self.city}, {self.country.name}"


class Currency(BaseModel):
    history = HistoricalRecords()
    symbol = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


class DividingFactor(BaseModel):
    history = HistoricalRecords()
    factor = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
