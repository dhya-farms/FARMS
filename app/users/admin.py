from django.contrib import admin
from django.contrib.auth import get_user_model

from app.users.forms import UserForm
from app.users.models import Bluetooth

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    # form = UserAdminChangeForm
    # add_form = UserAdminCreationForm

    readonly_fields = (
        'app_version_code',
    )
    fields = ["name", "mobile_no", "email", "designation", "date_joined", "app_version_code", "is_superuser"]
    form = UserForm
    # fieldsets = (
    #     ("Personal info", {"fields": ("name", 'phone_number', "email", "designation")}),
    #     (
    #         "Permissions",
    #         {
    #             "fields": (
    #                 "is_active",
    #                 "is_staff",
    #                 "is_superuser",
    #                 "groups",
    #                 "user_permissions",
    #             ),
    #         },
    #     ),
    #     ("Important dates", {"fields": ("last_login", "date_joined")}),
    # )
    list_display = ["id", "name", "mobile_no", "email", "designation", "is_superuser"]
    search_fields = ["name"]

    class Meta:
        model = User


# admin.site.register(User, UserAdmin)
admin.site.register(User)
admin.site.register(Bluetooth)
