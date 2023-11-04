from django.contrib import admin

from app.organizations.models import Organization, Place, ExpenseType

# Register your models here.
admin.site.register(Organization)
admin.site.register(Place)
admin.site.register(ExpenseType)
