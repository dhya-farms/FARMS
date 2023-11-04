from django.core import validators
from django.db import models
from django.urls import reverse

from app.fish.enums import WeightUnit
from app.organizations.enums import PlaceType

# Create a list of choices for the 'type' field with only 'Retail', 'Market', and 'Merchant' options for Sales
SALES_TYPE_CHOICES = [(PlaceType.RETAIL, 'Retail'), (PlaceType.MARKET, 'Market'), (PlaceType.MERCHANT, 'Merchant')]


class Fish(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name="fishes")
    is_active = models.BooleanField(default=True)
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}. name: {self.name} org:{self.organization}"


class FishVariant(models.Model):
    name = models.CharField(max_length=255)
    fish = models.ForeignKey('fish.Fish', on_delete=models.CASCADE, related_name="variants")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ],
        blank=True,
        null=True
    )
    weight_unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KILOGRAMS
    )
    is_active = models.BooleanField(default=True)
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"id: {self.id}. fish: {self.fish.name} variant: [{self.name}]"

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("fish:detail", kwargs={"pk": self.id})


class Discount(models.Model):
    name = models.CharField(max_length=255)
    discount = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            validators.MaxValueValidator(100)
        ]
    )
    type = models.IntegerField(choices=SALES_TYPE_CHOICES, blank=True, null=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name="discounts")
    is_active = models.BooleanField(default=True)
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"id: {self.id}. name: {self.name} type: {self.type}"


class PriceHistory(models.Model):
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(0.0)  # Ensure the price is non-negative
        ]
    )
    effective_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True,
                             null=True, related_name='price_history')
    fish_variant = models.ForeignKey('fish.FishVariant', on_delete=models.SET_NULL,
                                     blank=True, null=True, related_name="price_history")

    def __str__(self):
        return f"id: {self.id}. changed price: {self.price} effective_time: {self.effective_time} user: {self.user.name}"
