from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from app.organizations.enums import PlaceType
from app.users.enums import Designation


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=10, unique=True, validators=[
        RegexValidator(regex=r'^\d{10}$', message="Provide Proper 10 digit Phone Number")],
                                 db_index=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    designation = models.IntegerField(choices=Designation.choices,
                                      null=True, blank=True, default=Designation.NOT_ASSIGNED)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.SET_NULL,
                                     related_name="users", blank=True, null=True)
    place = models.ForeignKey('organizations.Place',
                              limit_choices_to={'type__in': [PlaceType.CENTER.value, PlaceType.RETAIL.value]},
                              on_delete=models.SET_NULL, related_name="users", blank=True, null=True)
    app_version_code = models.IntegerField(null=True, blank=True)

    REQUIRED_FIELDS = []

    def __str__(self):
        return f"id: {self.id}. {self.name} [{self.mobile_no}]"

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"mobile_no": self.mobile_no})


class Bluetooth(models.Model):
    name = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=17)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='bluetooth')
    # Moderation Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"id: {self.id}. name: {self.name} mac: {self.mac_address}] use: {self.user}"
