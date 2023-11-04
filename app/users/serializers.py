from django.contrib.auth import get_user_model
from rest_framework import serializers

from app.organizations.serializers import OrganizationSerializer, PlaceSerializer
from app.users.enums import Designation
from app.utils.helpers import get_serialized_enum

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    place = PlaceSerializer()
    designation = serializers.SerializerMethodField()

    # Helper Functions
    def get_designation(self, obj):
        if obj.designation:
            return get_serialized_enum(Designation(obj.designation))
        return dict()

    class Meta:
        model = User
        fields = ('id', 'name', 'mobile_no', 'email', 'designation',
                  'organization', 'place', 'is_active', 'last_login',
                  'date_joined')
