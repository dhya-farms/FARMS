from decimal import Decimal
from django.core import validators
from django.db import models
from app.fish.enums import WeightUnit
from app.logistics.enums import PayType, RecordType
from app.organizations.enums import PlaceType
from app.users.enums import Designation


class Record(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name="records")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='records')
    import_from = models.ForeignKey('organizations.Place', on_delete=models.SET_NULL,
                                    blank=True, null=True, related_name='exports')
    export_to = models.ForeignKey('organizations.Place', on_delete=models.SET_NULL,
                                  blank=True, null=True, related_name='imports')
    record_type = models.IntegerField(choices=RecordType.choices)
    discount = models.ForeignKey('fish.Discount', on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name='records')
    fish_variant = models.ForeignKey('fish.FishVariant', on_delete=models.SET_NULL,
                                     blank=True, null=True, related_name='records')
    weigh_place = models.ForeignKey('organizations.Place', on_delete=models.SET_NULL,
                                    blank=True, null=True, related_name='records')
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0)
        ]
    )
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KILOGRAMS
    )
    is_SP = models.BooleanField(default=False, help_text="Whether this import/export is damaged")
    is_active = models.BooleanField(default=True)
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"id: {self.id}. user: {self.user.name} from: {self.import_from.name} to: {self.export_to.name}" \
               f" applied discount: {self.discount.name} fish variant: {self.fish_variant} is_sp: {self.is_SP} " \
               f"weight: {self.weight} weight unit: {self.weight_unit}"


class Bill(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name="bills")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                             limit_choices_to={'designation': Designation.BILLER.value},
                             blank=True, null=True, related_name='bills')
    bill_place = models.ForeignKey('organizations.Place', on_delete=models.SET_NULL, blank=True, null=True,
                                   limit_choices_to={'type': PlaceType.RETAIL.value},
                                   related_name="bills")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ]
    )
    discount = models.ForeignKey('fish.Discount', on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name='bills')
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ]
    )
    billed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ]
    )
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ]
    )
    pay_type = models.IntegerField(choices=PayType.choices, default=PayType.CASH)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BillItem(models.Model):
    bill = models.ForeignKey('logistics.Bill', on_delete=models.SET_NULL,
                             blank=True, null=True, related_name='bill_items')
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0)
        ]
    )
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KILOGRAMS
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ]
    )
    fish_variant = models.ForeignKey('fish.FishVariant', on_delete=models.SET_NULL,
                                     blank=True, null=True, related_name='bill_items')
    is_SP = models.BooleanField(default=False, help_text="Whether this import/export is damaged")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"id: {self.id}. bill: {self.bill} fish variant: {self.fish_variant} is_sp: {self.is_SP} " \
               f"weight: {self.weight} weight unit: {self.weight_unit}"


class Stock(models.Model):
    place = models.ForeignKey('organizations.Place',
                              limit_choices_to={'type__in': [PlaceType.CENTER.value, PlaceType.RETAIL.value]},
                              on_delete=models.SET_NULL, related_name="stocks", blank=True, null=True)
    fish_variant = models.ForeignKey('fish.FishVariant', on_delete=models.SET_NULL,
                                     blank=True, null=True, related_name='stocks')
    is_SP = models.BooleanField(default=False, help_text="Whether this import/export is damaged")
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0)
        ],
        default=Decimal(0)
    )
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KILOGRAMS
    )
    updated_at = models.DateTimeField(auto_now=True)


class Expense(models.Model):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name="expenses")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL,
                             limit_choices_to={'designation': Designation.BILLER.value},
                             blank=True, null=True, related_name='expenses')
    type = models.ForeignKey('organizations.ExpenseType', on_delete=models.SET_NULL, blank=True, null=True,
                             related_name='expenses')
    desc = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0)
        ]
    )
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
