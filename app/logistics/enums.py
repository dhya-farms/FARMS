from enum import unique
from django.db import models


@unique
class PayType(models.IntegerChoices):
    CASH = 1, 'Cash'
    ONLINE = 2, 'GPay'


@unique
class RecordType(models.IntegerChoices):
    IMPORT = 1, 'Import'
    EXPORT = 2, 'Export'
