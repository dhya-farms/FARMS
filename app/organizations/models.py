from django.core.validators import RegexValidator
from django.db import models

from app.organizations.enums import PlaceType


class Organization(models.Model):
    name = models.CharField(max_length=255)
    logo = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"id: {self.id}. {self.name}"


class Place(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    mobile_no = models.CharField(max_length=10, validators=[
        RegexValidator(regex=r'^\d{10}$', message="Provide Proper 10 digit Phone Number")], blank=True, null=True)
    type = models.IntegerField(choices=PlaceType.choices, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name="places")
    center = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                               limit_choices_to={'type': PlaceType.CENTER.value},
                               related_name="landings")
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"id: {self.id}. {self.name} [{self.mobile_no}]"


class ExpenseType(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE,
                                     related_name="expense_types")
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
