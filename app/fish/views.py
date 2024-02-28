from django.core.cache import cache
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from app.fish.controllers import FishController, FishVariantController, DiscountController, PriceHistoryController
from app.fish.schemas import FishCreationReqSchema, FishEditReqSchema, FishListingReqSchema, \
    FishVariantCreationReqSchema, FishVariantEditReqSchema, FishVariantListingReqSchema, DiscountCreationReqSchema, \
    DiscountEditReqSchema, DiscountListingReqSchema, PriceHistoryListingSchema
from app.fish.serializers import DiscountSerializer, FishVariantSerializer, FishSerializer, PriceHistorySerializer
from app.utils.authentication import IsOrganizationUser
from app.utils.constants import Timeouts, CacheKeys
from app.utils.helpers import qdict_to_dict, build_cache_key
from app.utils.pagination import CustomPageNumberPagination


class FishViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = FishController()
    fish_variant_controller = FishVariantController()
    price_history_controller = PriceHistoryController()
    serializer = FishSerializer
    fish_variant_serializer = FishVariantSerializer
    price_history_serializer = PriceHistorySerializer

    @extend_schema(
        description="""
        Serves POST requests given on the entity API root path for Fish object creation
        This creates Fish Row in database and Mainly handles the requests coming from app
        """,
        request=FishCreationReqSchema,
        examples=[
            OpenApiExample('Fish Creation Request JSON', value={
                "name": "Sample Fish",
                "organization_id": 1,
                "is_active": True
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        """
        Serves POST requests given on the entity API root path for Fish object creation
        This creates Fish Row in database.

        POST /api/fish/
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(FishCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        # Create Fish
        errors, fish = self.controller.create_fish(
            name=data.name,
            organization_id=data.organization_id or user.organization_id,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": fish.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description=""" Partial updates the existing Fish
            """,
        request=FishEditReqSchema,
        examples=[
            OpenApiExample('Fish Edit Request JSON', value={
                "name": "Sample Fish",
                "organization_id": 1,
                "is_active": True
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        # Parsing request
        errors, data = self.controller.parse_request(FishEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract previous fish object
        fish = self.controller.get_instance_by_pk(pk=pk)
        if not fish:
            return JsonResponse({"error": "fish with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        user = request.user
        # Update User
        errors, fish = self.controller.edit_fish(
            fish=fish,
            name=data.name,
            organization_id=data.organization_id or user.organization_id,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": fish.pk,
            "message": "fish profile updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves GET requests, provide list and filter of Fish.
        GET /api/fish/
        :param request:
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='name', location=OpenApiParameter.QUERY, required=False,
                             type=str,
                             description='name'),
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='organization_id'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='is_active'),
        ],
    )
    def list(self, request, **kwargs):
        """
        Serves GET requests given on the entity API root path.
        GET /api/fish/
        :param request:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(FishListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginate queryset
        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        cache_key = build_cache_key(
            CacheKeys.FISH_LIST,
            name=data.name,
            organization_id=data.organization_id or user.organization.id,
            is_active=data.is_active,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None
        # Get and Filter
        if instance:
            res = instance
        else:
            errors, data = self.controller.filter_fish(
                name=data.name,
                organization_id=data.organization_id or user.organization.id,
                is_active=data.is_active,
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(data, request)
            if page is None:
                page = data

            # Serialize data
            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="""
        Serves GET requests coming for a particular entity by id `pk`
        GET /api/fish/<pk>
        :param request:
        :param pk: Primary Key for user entity as path parameter
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='pk'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        """
        Serves GET requests coming for a particular entity by id `pk`
        GET /api/fish/<pk>
        :param request:
        :param pk: Primary Key for fish entity as path parameter
        :param kwargs:
        :return:
        """
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.FISH_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return JsonResponse({"error": "fish with this id does not exists"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves POST requests to make a fish inactive.
        POST /api/fish/<id>/make-inactive/
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='pk'),
        ],
    )
    @action(methods=['POST'], detail=True)
    def make_inactive(self, request, pk, *args, **kwargs):
        obj = self.controller.get_instance_by_pk(pk=pk)
        if not obj:
            return JsonResponse({"error": "Obj with this ID does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        errors, data = self.controller.make_inactive(obj)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(data={'message': "Successfully inactivated."}, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves GET requests to get list and filter of fish variants of specific fish.
        GET /api/fish/<id>/fish_variants/
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='pk'),
        ],
    )
    @action(methods=['GET'], detail=True)
    def fish_variants(self, request, pk, *args, **kwargs):
        # Paginate queryset
        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE

        fish = self.controller.get_instance_by_pk(pk=pk)
        if not fish:
            return JsonResponse({"error": "fish with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        errors, data = self.fish_variant_controller.get_fish_variants_with_fish(
            fish=fish
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        page = paginator.paginate_queryset(data, request)
        if page is None:
            page = data

        # Serialize data
        data = self.fish_variant_controller.serialize_queryset(page, self.fish_variant_serializer)
        result = paginator.get_paginated_response(data)
        return result

    @extend_schema(
        description="Filter and list price histories",
        parameters=[
            OpenApiParameter(name='user_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='ID of the user'),
            OpenApiParameter(name='fish_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='ID of the fish'),
            OpenApiParameter(name='fish_variant', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Variant of the fish'),
            OpenApiParameter(name='start_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Start time for the price history'),
            OpenApiParameter(name='end_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='End time for the price history'),
        ],
    )
    @action(methods=['GET'], detail=False)
    def price_histories(self, request, *args, **kwargs):
        # Parsing request
        errors, data = self.controller.parse_request(PriceHistoryListingSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginate queryset
        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE

        cache_key = build_cache_key(
            CacheKeys.PRICE_HISTORY_LIST,
            user_id=data.user_id,
            fish_id=data.fish_id,
            fish_variant=data.fish_variant_id,
            start_time=data.get_start_time(),
            end_time=data.get_end_time(),
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None
        # Get and Filter
        if instance:
            res = instance
        else:
            errors, data = self.price_history_controller.filter_price_histories(
                user_id=data.user_id,
                fish_id=data.fish_id,
                fish_variant_id=data.fish_variant_id,
                start_time=data.get_start_time(),
                end_time=data.get_end_time(),
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(data, request)
            if page is None:
                page = data

            # Serialize data
            data = self.price_history_controller.serialize_queryset(page, self.price_history_serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result


class FishVariantViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = FishVariantController()
    serializer = FishVariantSerializer

    @extend_schema(
        description="""
        Serves POST requests for creating a new fish variant.
        This endpoint creates a fish variant in the database.
        Mainly handles the requests coming from the app.
        """,
        request=FishVariantCreationReqSchema,
        examples=[
            OpenApiExample('Fish Variant Creation Request JSON', value={
                "fish_id": 1,
                "name": "Sample Fish Variant",
                "price": 10.99,
                "weight_unit": "KG",
                "is_active": True
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        """
        Serves POST requests for creating a new fish variant.
        This creates a fish variant in the database and handles requests from the app.

        POST /api/fish_variants/
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(FishVariantCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Create Fish Variant
        errors, fish_variant = self.controller.create_fish_variant(
            fish_id=data.fish_id,
            name=data.name,
            price=data.price,
            weight_unit=data.weight_unit,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": fish_variant.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description=""" Partially update an existing fish variant.
            """,
        request=FishVariantEditReqSchema,
        examples=[
            OpenApiExample('Fish Variant Edit Request JSON', value={
                "fish_id": 2,
                "name": "Edited Fish Variant",
                "price": 15.99,
                "weight_unit": "LB",
                "is_active": False
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        # Parsing request
        errors, data = self.controller.parse_request(FishVariantEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Get the existing fish variant
        fish_variant = self.controller.get_instance_by_pk(pk=pk)
        if not fish_variant:
            return JsonResponse({"error": "fish variant with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)

        # Update Fish Variant
        errors, fish_variant = self.controller.edit_fish_variant(
            fish_variant=fish_variant,
            fish_id=data.fish_id,
            name=data.name,
            price=data.price,
            weight_unit=data.weight_unit,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": fish_variant.pk,
            "message": "Fish variant updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Filter and list fish variants",
        parameters=[
            OpenApiParameter(name='fish_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='ID of the fish'),
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='ID of the organization'),
            OpenApiParameter(name='name', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Name of the fish variant'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Active status of the fish variant'),
        ],
    )
    def list(self, request, **kwargs):
        """
        Serves GET requests for a list of fish variants.
        GET /api/fish_variants/
        :param request:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(FishVariantListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginate queryset
        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        cache_key = build_cache_key(
            CacheKeys.FISH_VARIANT_LIST,
            fish_id=data.fish_id,
            name=data.name,
            organization_id=data.organization_id or user.organization.id,
            is_active=data.is_active,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None
        # Get and Filter
        if instance:
            res = instance
        else:
            errors, fish_variants = self.controller.filter_fish_variants(
                fish_id=data.fish_id,
                organization_id=data.organization_id or user.organization.id,
                name=data.name,
                is_active=data.is_active,
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(fish_variants, request)
            if page is None:
                page = data

            # Serialize data
            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="""
        Serves GET requests for a particular fish variant by ID.
        GET /api/fish_variants/<pk>
        :param request:
        :param pk: Primary Key for fish variant entity as path parameter
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        """
        Serves GET requests for a particular fish variant by ID.
        GET /api/fish_variants/<pk>
        :param request:
        :param pk: Primary Key for fish variant entity as path parameter
        :param kwargs:
        :return:
        """
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.FISH_VARIANT_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return JsonResponse({"error": "Fish variant with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves POST requests for a particular fish variant to make inactive.
        POST /api/fish_variants/<id>/make-inactive/
        :param request:
        :param pk: Primary Key for fish variant entity as path parameter
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    @action(methods=['POST'], detail=True)
    def make_inactive(self, request, pk, *args, **kwargs):
        """
        Serves POST requests to make a fish variant inactive.
        POST /api/fish_variants/<id>/make-inactive/
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        obj = self.controller.get_instance_by_pk(pk=pk)
        if not obj:
            return JsonResponse({"error": "Obj with this ID does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        errors, data = self.controller.make_inactive(obj)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(data={'message': "Successfully inactivated."}, status=status.HTTP_200_OK)


class DiscountViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = DiscountController()
    serializer = DiscountSerializer

    @extend_schema(
        description="""
        Serves POST requests for creating a discount.
        POST /api/discounts/
        """,
        request=DiscountCreationReqSchema,
        examples=[
            OpenApiExample('Discount Creation Request JSON', value={
                "name": "Sample Discount",
                "discount": 10,
                "type": 1,
                "organization_id": 1,
                "is_active": True
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(DiscountCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        errors, discount = self.controller.create_discount(
            name=data.name,
            discount=data.discount,
            type=data.type,
            organization_id=data.organization_id or user.organization_id,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": discount.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Partial update of an existing discount.",
        request=DiscountEditReqSchema,
        examples=[
            OpenApiExample('Discount Edit Request JSON', value={
                "name": "Updated Discount",
                "discount": 15,
                "type": 2,
                "organization_id": 1,
                "is_active": True
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(DiscountEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        discount_obj = self.controller.get_instance_by_pk(pk=pk)
        if not discount_obj:
            return JsonResponse({"error": "Discount with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, discount_obj = self.controller.edit_discount(
            discount_obj=discount_obj,
            name=data.name,
            discount=data.discount,
            type=data.type,
            organization_id=data.organization_id or user.organization_id,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": discount_obj.pk,
            "message": "Discount profile updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Retrieve a list of discounts based on filtering criteria.",
        request=DiscountListingReqSchema,
        parameters=[
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Organization ID'),
            OpenApiParameter(name='name', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Name'),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, required=False,
                             type=int,
                             description='Type'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=True, type=bool,
                             description='Is Active'),
        ],
    )
    def list(self, request, **kwargs):
        """
        Serves GET requests for a list of discounts.
        GET /api/discounts/
        :param request:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(DiscountListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginate queryset
        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        cache_key = build_cache_key(
            CacheKeys.DISCOUNT_LIST,
            organization_id=data.organization_id or user.organization.id,
            name=data.name,
            type=data.type,
            is_active=data.is_active,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None
        # Get and Filter
        if instance:
            res = instance
        else:
            # Filter discounts based on the provided criteria
            errors, discount_qs = self.controller.filter_discounts(
                organization_id=data.organization_id or user.organization.id,
                name=data.name,
                type=data.type,
                is_active=data.is_active,
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(discount_qs, request)
            if page is None:
                page = data

            # Serialize data
            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="Retrieve a specific discount by ID.",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='Discount ID'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        # Retrieve a specific discount by ID
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.DISCOUNT_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None

        if instance:
            data = instance
        else:
            discount_obj = self.controller.get_instance_by_pk(pk=pk)
            if not discount_obj:
                return JsonResponse({"error": "Discount with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(discount_obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)

        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves POST requests to make a discount inactive by its ID.
        POST /api/discounts/<pk>/make_inactive
        """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='Discount ID'),
        ],
    )
    @action(methods=['POST'], detail=True)
    def make_inactive(self, request, pk, *args, **kwargs):
        obj = self.controller.get_instance_by_pk(pk=pk)
        if not obj:
            return JsonResponse({"error": "Obj with this ID does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
        errors, data = self.controller.make_inactive(obj)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(data={'message': "Successfully inactivated."}, status=status.HTTP_200_OK)
