from rest_framework import serializers

from app.fish.enums import WeightUnit
from app.fish.models import Fish, FishVariant, Discount, PriceHistory
from app.fish.serializers import DiscountSerializer, FishVariantSerializer, FishSerializer
from app.logistics.enums import PayType, RecordType
from app.logistics.models import Record, BillItem, Bill, Stock, Expense
from app.organizations.enums import PlaceType
from app.organizations.serializers import OrganizationSerializer, PlaceSerializer, ExpenseTypeSerializer
from app.users.serializers import UserSerializer
from app.utils.helpers import get_serialized_enum


class RecordSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    import_from = PlaceSerializer()
    export_to = PlaceSerializer()
    record_type = serializers.SerializerMethodField()
    discount = DiscountSerializer()
    fish = FishSerializer()
    fish_variant = FishVariantSerializer()
    weigh_place = PlaceSerializer()
    weight_unit = serializers.SerializerMethodField()

    def get_weight_unit(self, obj: Record):
        if obj.weight_unit:
            return get_serialized_enum(WeightUnit(obj.weight_unit))
        return dict()

    def get_record_type(self, obj: Record):
        if obj.weight_unit:
            return get_serialized_enum(RecordType(obj.record_type))
        return dict()

    class Meta:
        model = Record
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    bill_place = PlaceSerializer()
    discount = DiscountSerializer()
    pay_type = serializers.SerializerMethodField()

    def get_pay_type(self, obj: Bill):
        if obj.pay_type:
            return get_serialized_enum(PayType(obj.pay_type))
        return dict()

    class Meta:
        model = Bill
        fields = '__all__'


class BillItemSerializer(serializers.ModelSerializer):
    bill = BillSerializer()
    fish = FishSerializer()
    fish_variant = FishVariantSerializer()
    weight_unit = serializers.SerializerMethodField()

    def get_weight_unit(self, obj: BillItem):
        if obj.weight_unit:
            return get_serialized_enum(WeightUnit(obj.weight_unit))
        return dict()

    class Meta:
        model = BillItem
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    fish = FishSerializer()
    fish_variant = FishVariantSerializer()
    weight_unit = serializers.SerializerMethodField()

    def get_weight_unit(self, obj: Stock):
        if obj.weight_unit:
            return get_serialized_enum(WeightUnit(obj.weight_unit))
        return dict()

    class Meta:
        model = Stock
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    type = ExpenseTypeSerializer()

    class Meta:
        model = Expense
        fields = '__all__'
