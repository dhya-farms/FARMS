from enum import unique
from django.db import models


@unique
class WeightUnit(models.TextChoices):
    KILOGRAMS = 'kg', 'Kilograms'
    GRAMS = 'g', 'Grams'
    POUNDS = 'lb', 'Pounds'
    TONNE = 't', 'Tonne'
    KILOTONNE = 'kt', 'KiloTonne'
