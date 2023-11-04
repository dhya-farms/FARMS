from typing import Optional

from django.conf import settings
from django.db.models import F, Q, Case, When, Value, Count
from django.utils import timezone
from django.utils import translation
from django.db import IntegrityError

from app.fish.enums import WeightUnit
from app.fish.models import Fish, FishVariant, Discount, PriceHistory
from app.fish.serializers import FishSerializer, FishVariantSerializer, DiscountSerializer, PriceHistorySerializer
from app.utils.controllers import Controller
from app.utils.helpers import get_serialized_exception


class FishController(Controller):
    def __init__(self):
        self.model = Fish

    def create_fish(self,
                    name,
                    organization_id,
                    is_active):
        """
        take attributes of user including designation and create user model in DB

        :param name:
        :param organization_id:
        :param is_active:
        """
        try:
            fish = self.model.objects.create(
                name=name,
                organization_id=organization_id,
                is_active=is_active
            )
            return None, fish
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_fish(self,
                  fish,
                  name,
                  organization_id,
                  is_active):
        """
        Update user model using the attributes specified
        :param fish:
        :param name:
        :param organization_id:
        :param is_active:
        """
        try:
            fish.name = name
            fish.organization_id = organization_id
            fish.is_active = is_active

            fish.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, fish

    def filter_fish(self,
                    name,
                    organization_id,
                    is_active,
                    ordering
                    ):
        fish_qs = self.get_valid_fish()
        try:
            if is_active:
                fish_qs = fish_qs.filter(is_active=is_active)
            if organization_id:
                fish_qs = fish_qs.filter(organization_id=organization_id)

            # Initialize an empty Q object to start the filter.
            query = Q()
            if name:
                query |= Q(name__icontains=name)

            fish_qs = fish_qs.filter(query)
            ordering = ordering if ordering is not None else 'name'
            if ordering:
                fish_qs = fish_qs.order_by(ordering)
            return None, fish_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_fish(self):
        return self.model.objects.all()

    def make_inactive(self, obj):
        try:
            errors, data = super().make_inactive(obj)
            if errors:
                return errors, data
            obj.variants.update(is_active=False)
            obj.save()
        except Exception as e:
            return get_serialized_exception(e)
        return None, True


class FishVariantController(Controller):
    def __init__(self):
        self.model = FishVariant

    def create_fish_variant(self,
                            fish_id,
                            name,
                            price,
                            weight_unit,
                            is_active):
        """
        take attributes of user including designation and create user model in DB
        :param fish_id:
        :param name:
        :param price:
        :param weight_unit:
        :param is_active:
        """
        try:
            fish_variant = self.model.objects.create(
                fish_id=fish_id,
                name=name,
                price=price,
                weight_unit=weight_unit,
                is_active=is_active
            )
            return None, fish_variant
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_fish_variant(self,
                          fish_variant,
                          fish_id,
                          name,
                          price,
                          weight_unit,
                          is_active):
        """
        Update user model using the attributes specified
        :param fish_variant:
        :param fish_id:
        :param name:
        :param price:
        :param weight_unit:
        :param is_active:
        """
        try:
            fish_variant.fish_id = fish_id
            fish_variant.name = name
            fish_variant.price = price
            fish_variant.weight_unit = weight_unit
            fish_variant.is_active = is_active

            fish_variant.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, fish_variant

    def filter_fish_variants(self,
                             fish_id,
                             organization_id,
                             name,
                             is_active,
                             ordering
                             ):
        fish_variant_qs = self.get_valid_fish_variants()
        try:
            if is_active:
                fish_variant_qs = fish_variant_qs.filter(is_active=is_active)

            if fish_id:
                fish_variant_qs = fish_variant_qs.filter(fish_id=fish_id)

            if organization_id:
                fish_variant_qs = fish_variant_qs.filter(fish__organization_id=organization_id,)

            # Initialize an empty Q object to start the filter.
            query = Q()
            if name:
                query |= Q(name__icontains=name)

            fish_variant_qs = fish_variant_qs.filter(query)

            ordering = ordering if ordering is not None else 'name'
            if ordering:
                fish_variant_qs = fish_variant_qs.order_by(ordering)
            return None, fish_variant_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_fish_variants_with_fish(self, fish):
        try:
            fish_variants = fish.variants.all()
            return None, fish_variants
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_fish_variants(self):
        return self.model.objects.select_related('fish').all()


class DiscountController(Controller):
    def __init__(self):
        self.model = Discount

    def create_discount(self,
                        name,
                        discount,
                        type,
                        organization_id,
                        is_active):
        """
        take attributes of user including designation and create user model in DB
        :param name:
        :param discount:
        :param type:
        :param organization_id:
        :param is_active:
        """
        try:
            discount = self.model.objects.create(
                name=name,
                discount=discount,
                type=type,
                organization_id=organization_id,
                is_active=is_active
            )
            return None, discount
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_discount(self,
                      discount_obj,
                      name,
                      discount,
                      type,
                      organization_id,
                      is_active):
        """
        Update user model using the attributes specified
        :param discount_obj
        :param name:
        :param discount:
        :param type:
        :param organization_id:
        :param is_active:
        """
        try:
            discount_obj.name = name
            discount_obj.discount = discount
            discount_obj.type = type
            discount_obj.organization_id = organization_id
            discount_obj.is_active = is_active

            discount_obj.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, discount_obj

    def filter_discounts(self,
                         organization_id,
                         name,
                         type,
                         is_active,
                         ordering
                         ):
        discount_qs = self.get_valid_discounts()

        try:
            if organization_id:
                discount_qs = discount_qs.filter(organization_id=organization_id)

            if is_active:
                discount_qs = discount_qs.filter(is_active=is_active)
            if type:
                discount_qs = discount_qs.filter(type=type)

            # Initialize an empty Q object to start the filter.
            query = Q()
            if name:
                query |= Q(name__icontains=name)

            discount_qs = discount_qs.filter(query)

            ordering = ordering if ordering is not None else '-created_at'
            if ordering:
                discount_qs = discount_qs.order_by(ordering)
            return None, discount_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_discounts(self):
        return self.model.objects.all()


class PriceHistoryController(Controller):
    def __init__(self):
        self.model = PriceHistory

    def filter_price_histories(self,
                               user_id,
                               fish_id,
                               fish_variant_id,
                               start_time,
                               end_time,
                               ordering
                               ):
        price_history_qs = self.get_valid_price_histories()
        try:
            if user_id:
                price_history_qs = price_history_qs.filter(user_id=user_id)
            if fish_id:
                price_history_qs = price_history_qs.filter(fish_variant__fish_id=fish_id)
            if fish_variant_id:
                price_history_qs = price_history_qs.filter(fish_variant=fish_variant_id)
            if start_time and end_time:
                price_history_qs = price_history_qs.filter(effective_time__range=(start_time, end_time))
            ordering = ordering if ordering is not None else '-effective_time'
            if ordering:
                price_history_qs = price_history_qs.order_by(ordering)

            return None, price_history_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_price_histories(self):
        return self.model.objects.select_related('fish_variant').all()
