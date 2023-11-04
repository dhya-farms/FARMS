from enum import unique
from django.db import models


@unique
class PlaceType(models.IntegerChoices):
    CENTER = 1, 'Center'
    LANDING = 2, 'Landing'
    RETAIL = 3, 'Retail'
    MARKET = 4, 'Market'
    MERCHANT = 5, 'Merchant'
