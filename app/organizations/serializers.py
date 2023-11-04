from rest_framework import serializers

from app.organizations.enums import PlaceType
from app.organizations.models import Organization, Place, ExpenseType
from app.utils.helpers import get_serialized_enum


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


# class CenterPlaceSerializer(serializers.ModelSerializer):
#     organization = OrganizationSerializer()
#
#     class Meta:
#         model = Place
#         exclude = ('type', 'organization', 'center')
#
#
# class PlaceSerializer(serializers.ModelSerializer):
#     organization = OrganizationSerializer()
#     center = CenterPlaceSerializer()
#
#     class Meta:
#         model = Place
#         fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    organization = OrganizationSerializer()
    center = serializers.SerializerMethodField()

    def get_center(self, obj: Place):
        # Check if the 'center' field is not None
        if obj.center:
            # Serialize the 'center' field using the same serializer (PlaceSerializer)
            return PlaceSerializer(obj.center, context=self.context).data
        return None

    def get_type(self, obj: Place):
        if obj.type:
            get_serialized_enum(PlaceType(obj.type))
        return dict()

    class Meta:
        model = Place
        fields = '__all__'


class ExpenseTypeSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = ExpenseType
        fields = '__all__'
