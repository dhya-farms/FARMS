from rest_framework import serializers

from app.fish.enums import WeightUnit
from app.fish.models import Fish, FishVariant, Discount, PriceHistory
from app.organizations.enums import PlaceType
from app.organizations.serializers import OrganizationSerializer
from app.users.serializers import UserSerializer
from app.utils.helpers import get_serialized_enum


class FishSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = Fish
        fields = '__all__'


class FishVariantSerializer(serializers.ModelSerializer):
    weight_unit = serializers.SerializerMethodField()

    def get_weight_unit(self, obj: FishVariant):
        if obj.weight_unit:
            return get_serialized_enum(WeightUnit(obj.weight_unit))
        return dict()

    class Meta:
        model = FishVariant
        exclude = ('fish', )


class DiscountSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    organization = OrganizationSerializer()

    def get_type(self, obj: Discount):
        if obj.type:
            return get_serialized_enum(PlaceType(obj.type))
        return dict()

    class Meta:
        model = Discount
        fields = '__all__'


class PriceHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    fish_variant = FishVariantSerializer()

    class Meta:
        model = PriceHistory
        fields = '__all__'
