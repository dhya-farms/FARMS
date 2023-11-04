from enum import unique
from django.db import models


@unique
class Designation(models.IntegerChoices):
    ADMIN = 1, 'Admin'
    WEIGHER = 2, 'Weigher'
    BILLER = 3, 'Biller'
    NOT_ASSIGNED = 4, 'Not Assigned'
