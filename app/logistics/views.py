from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from app.logistics.controllers import RecordController, ExpenseController, BillController, BillItemController, \
    StockController
from app.logistics.enums import RecordType
from app.logistics.schemas import RecordCreationReqSchema, RecordEditReqSchema, RecordListingReqSchema, \
    ExpenseCreationReqSchema, ExpenseEditReqSchema, ExpenseListingReqSchema, BillListingReqSchema, BillEditReqSchema, \
    BillCreationReqSchema, BillItemCreationReqSchema, BillItemEditReqSchema, BillItemListingReqSchema, \
    StockCreationReqSchema, StockEditReqSchema, StockListingReqSchema, AddToStockSchema
from app.logistics.serializers import RecordSerializer, ExpenseSerializer, BillSerializer, BillItemSerializer, \
    StockSerializer
from app.utils.authentication import IsOrganizationUser
from app.utils.constants import Timeouts, CacheKeys
from app.utils.helpers import get_serialized_exception, build_cache_key, qdict_to_dict
from app.utils.pagination import CustomPageNumberPagination


class RecordViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = RecordController()
    stock_controller = StockController()

    serializer = RecordSerializer
    stock_serializer = StockSerializer

    @extend_schema(
        description="Create a new record",
        request=RecordCreationReqSchema,
        examples=[
            OpenApiExample('Record Creation Request JSON', value={
                "organization_id": 1,
                "user_id": 1,
                "import_from_id": 1,
                "export_to_id": 2,
                "record_type": 1,
                "discount_id": 1,
                "fish_id": 1,
                "fish_variant_id": 1,
                "weigh_place_id": 3,
                "weight": 10.5,
                "weight_unit": 1,
                "is_SP": False,
                "is_active": True
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(RecordCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        errors, record = self.controller.create_record(
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id or user.id,
            import_from_id=data.import_from_id,
            export_to_id=data.export_to_id,
            record_type=data.record_type,
            discount_id=data.discount_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            weigh_place_id=data.weigh_place_id,
            weight=data.weight,
            weight_unit=data.weight_unit,
            is_SP=data.is_SP,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": record.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Add to Landings",
        request=RecordCreationReqSchema,
        examples=[
            OpenApiExample('Add To Landings Request JSON', value={
                "organization_id": 1,
                "user_id": 1,
                "import_from_id": 1,
                "export_to_id": 2,
                "record_type": 1,
                "discount_id": 1,
                "fish_id": 1,
                "fish_variant_id": 1,
                "weigh_place_id": 3,
                "weight": 10.5,
                "weight_unit": 1,
                "is_SP": False,
                "is_active": True
            })
        ]
    )
    @action(methods=['POST'], detail=False)
    def add_to_landings(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(RecordCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        try:
            with transaction.atomic():
                errors, record_import = self.controller.create_record(
                    organization_id=data.organization_id or user.organization.id,
                    user_id=data.user_id or user.id,
                    import_from_id=data.import_from_id,
                    export_to_id=user.place.id,
                    record_type=RecordType.IMPORT,
                    discount_id=data.discount_id,
                    fish_id=data.fish_id,
                    fish_variant_id=data.fish_variant_id,
                    weigh_place_id=user.place.id,
                    weight=data.weight,
                    weight_unit=data.weight_unit,
                    is_SP=data.is_SP,
                    is_active=data.is_active
                )
                if errors:
                    return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
                if data.export_to_id is not None:
                    errors, record_export = self.controller.create_record(
                        organization_id=user.organization.id,
                        user_id=user.id,
                        import_from_id=user.place.id,
                        export_to_id=data.export_to_id,
                        record_type=RecordType.EXPORT,
                        discount_id=data.discount_id,
                        fish_id=data.fish_id,
                        fish_variant_id=data.fish_variant_id,
                        weigh_place_id=user.place.id,
                        weight=data.weight,
                        weight_unit=data.weight_unit,
                        is_SP=data.is_SP,
                        is_active=data.is_active
                    )
                    if errors:
                        raise Exception(errors)

                    data = {
                        "import_id": record_import.pk,
                        "export_id": record_export.pk,
                    }
                    return JsonResponse(data=data, status=status.HTTP_201_CREATED)
                else:
                    errors, stock = self.stock_controller.update_stock_weight(
                        place_id=user.place.id,
                        fish_id=data.fish_id,
                        fish_variant_id=data.fish_variant_id,
                        is_SP=data.is_SP,
                        weight=data.weight,
                        weight_unit=data.weight_unit,
                    )
                    if errors:
                        raise Exception(errors)

                    data = {
                        "record_id": record_import.pk,
                        "stock_id": stock.pk,
                    }
                    return JsonResponse(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse(data=get_serialized_exception(e)[0], status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Add to Sales",
        request=RecordCreationReqSchema,
        examples=[
            OpenApiExample('Add to Sales to Sales Request JSON', value={
                "organization_id": 1,
                "user_id": 1,
                "import_from_id": 1,
                "export_to_id": 2,
                "record_type": 1,
                "discount_id": 1,
                "fish_id": 1,
                "fish_variant_id": 1,
                "weigh_place_id": 3,
                "weight": 10.5,
                "weight_unit": 1,
                "is_SP": False,
                "is_active": True
            })
        ]
    )
    @action(methods=['POST'], detail=False)
    def add_to_sales(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(RecordCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        try:
            with transaction.atomic():
                errors, record = self.controller.create_record(
                    organization_id=user.organization.id,
                    user_id=user.id,
                    import_from_id=user.place.id,
                    export_to_id=data.export_to_id,
                    record_type=RecordType.EXPORT,
                    discount_id=data.discount_id,
                    fish_id=data.fish_id,
                    fish_variant_id=data.fish_variant_id,
                    weigh_place_id=user.place.id,
                    weight=data.weight,
                    weight_unit=data.weight_unit,
                    is_SP=data.is_SP,
                    is_active=data.is_active
                )
                if errors:
                    return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
                errors, stock = self.stock_controller.update_stock_weight(
                    place_id=user.place.id,
                    fish_id=data.fish_id,
                    fish_variant_id=data.fish_variant_id,
                    is_SP=data.is_SP,
                    weight=-abs(data.weight),
                    weight_unit=data.weight_unit,
                )
                if errors:
                    raise Exception(errors)

                data = {
                    "record_id": record.pk,
                    "stock_id": stock.pk,
                }
                return JsonResponse(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse(data=get_serialized_exception(e)[0], status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Send Stock From one Place to other",
        request=RecordCreationReqSchema,
        examples=[
            OpenApiExample('Send Stock Request JSON', value={
                "organization_id": 1,
                "user_id": 1,
                "import_from_id": 1,
                "export_to_id": 2,
                "record_type": 1,
                "discount_id": 1,
                "fish_id": 1,
                "fish_variant_id": 1,
                "weigh_place_id": 3,
                "weight": 10.5,
                "weight_unit": 1,
                "is_SP": False,
                "is_active": True
            })
        ]
    )
    @action(methods=['POST'], detail=False)
    def send_stock(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(RecordCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        try:
            with transaction.atomic():
                errors, record = self.controller.create_record(
                    organization_id=user.organization.id,
                    user_id=user.id,
                    import_from_id=user.place.id,
                    export_to_id=data.export_to_id,
                    record_type=RecordType.EXPORT,
                    discount_id=data.discount_id,
                    fish_id=data.fish_id,
                    fish_variant_id=data.fish_variant_id,
                    weigh_place_id=user.place.id,
                    weight=data.weight,
                    weight_unit=data.weight_unit,
                    is_SP=data.is_SP,
                    is_active=data.is_active
                )
                if errors:
                    return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
                errors, stock = self.stock_controller.update_stock_weight(
                    place_id=user.place.id,
                    fish_id=data.fish_id,
                    fish_variant_id=data.fish_variant_id,
                    is_SP=data.is_SP,
                    weight=-abs(data.weight),
                    weight_unit=data.weight_unit,
                )
                if errors:
                    raise Exception(errors)

                data = {
                    "record_id": record.pk,
                    "stock_id": stock.pk,
                }
                return JsonResponse(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse(data=get_serialized_exception(e)[0], status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Add to Stock received from other place",
        request=RecordCreationReqSchema,
        examples=[
            OpenApiExample('Add to Stock Request JSON', value={
                "organization_id": 1,
                "user_id": 1,
                "import_from_id": 1,
                "export_to_id": 2,
                "record_type": 1,
                "discount_id": 1,
                "fish_id": 1,
                "fish_variant_id": 1,
                "weigh_place_id": 3,
                "weight": 10.5,
                "weight_unit": 1,
                "is_SP": False,
                "is_active": True
            })
        ]
    )
    @action(methods=['POST'], detail=False)
    def add_to_stock(self, request, *args, **kwargs):
        errors, data_all = self.controller.parse_request(AddToStockSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        try:
            result = []
            for data in data_all.items:
                with transaction.atomic():
                    errors, record = self.controller.create_record(
                        organization_id=user.organization.id,
                        user_id=user.id,
                        import_from_id=data.import_from_id,
                        export_to_id=user.place.id,
                        record_type=RecordType.IMPORT,
                        discount_id=data.discount_id,
                        fish_id=data.fish_id,
                        fish_variant_id=data.fish_variant_id,
                        weigh_place_id=user.place.id,
                        weight=data.weight,
                        weight_unit=data.weight_unit,
                        is_SP=data.is_SP,
                        is_active=data.is_active
                    )
                    if errors:
                        return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
                    errors, stock = self.stock_controller.update_stock_weight(
                        place_id=user.place.id,
                        fish_id=data.fish_id,
                        fish_variant_id=data.fish_variant_id,
                        is_SP=data.is_SP,
                        weight=data.weight,
                        weight_unit=data.weight_unit,
                    )
                    if errors:
                        raise Exception(errors)

                    item_result = {
                        "record_id": record.pk,
                        "stock_id": stock.pk,
                    }
                    result.append(item_result)
            return JsonResponse(data={"result": result}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse(data=get_serialized_exception(e)[0], status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Edit an existing record",
        request=RecordEditReqSchema,
        examples=[
            OpenApiExample('Record Edit Request JSON', value={
                "user_id": 2,
                "import_from_id": 3,
                "export_to_id": 4,
                "record_type": 1,
                "discount_id": 2,
                "fish_id": 1,
                "fish_variant_id": 2,
                "weigh_place_id": 5,
                "weight": 15.0,
                "weight_unit": "LB",
                "is_SP": True,
                "is_active": False
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(RecordEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        record = self.controller.get_instance_by_pk(pk=pk)
        if not record:
            return JsonResponse({"error": "record with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, record = self.controller.edit_record(
            record_obj=record,
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id or user.id,
            import_from_id=data.import_from_id,
            export_to_id=data.export_to_id,
            record_type=data.record_type,
            discount_id=data.discount_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            weigh_place_id=data.weigh_place_id,
            weight=data.weight,
            weight_unit=data.weight_unit,
            is_SP=data.is_SP,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": record.pk,
            "message": "Record updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Retrieve a list of records with optional filters",
        request=RecordListingReqSchema,
        parameters=[
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=True, type=int,
                             description='Organization ID'),
            OpenApiParameter(name='user_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='User ID'),
            OpenApiParameter(name='import_from_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Import From ID'),
            OpenApiParameter(name='export_to_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Export To ID'),
            OpenApiParameter(name='record_type', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Record Type(Import/Eport)'),
            OpenApiParameter(name='discount_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Discount ID'),
            OpenApiParameter(name='fish_variant_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Fish Variant ID'),
            OpenApiParameter(name='weigh_place_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Weigh Place ID'),
            OpenApiParameter(name='is_SP', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Is SP'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Is Active'),
            OpenApiParameter(name='start_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Start time for filtering'),
            OpenApiParameter(name='end_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='End Time for filtering')
        ]
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(RecordListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        cache_key = build_cache_key(
            CacheKeys.RECORD_LIST,
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id,
            import_from_id=data.import_from_id,
            export_to_id=data.export_to_id,
            record_type=data.record_type,
            discount_id=data.discount_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            weigh_place_id=data.weigh_place_id,
            is_SP=data.is_SP,
            is_active=data.is_active,
            start_time=data.get_start_time(),
            end_time=data.get_end_time(),
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None

        if instance:
            res = instance
        else:
            errors, records = self.controller.filter_records(
                organization_id=data.organization_id or user.organization.id,
                user_id=data.user_id,
                import_from_id=data.import_from_id,
                export_to_id=data.export_to_id,
                record_type=data.record_type,
                discount_id=data.discount_id,
                fish_id=data.fish_id,
                fish_variant_id=data.fish_variant_id,
                weigh_place_id=data.weigh_place_id,
                is_SP=data.is_SP,
                is_active=data.is_active,
                start_time=data.get_start_time(),
                end_time=data.get_end_time(),
                ordering=data.ordering,
            )

            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(records, request)
            if page is None:
                page = records

            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

    def retrieve(self, request, pk, *args, **kwargs):
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.RECORD_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)

            if not obj:
                return JsonResponse({"error": "Record with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Make a record inactive"
                    "POST /api/records/<id>/make-inactive/",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='Record ID')
        ]
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


class BillViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = BillController()
    bill_item_controller = BillItemController()
    serializer = BillSerializer
    bill_item_serializer = BillItemSerializer
    stock_controller = StockController()
    stock_serializer = StockSerializer

    @extend_schema(
        description="Create a new bill.",
        request=BillCreationReqSchema,
        examples=[
            OpenApiExample('Bill Creation Request JSON', value={
                "bill_items": [
                    {
                        "weight": 10.5,
                        "weight_unit": "KG",
                        "price": 100.99,
                        "fish_id": 1,
                        "fish_variant_id": 2,
                        "is_SP": False,
                        "is_active": True
                    },
                    {
                        "weight": 10.5,
                        "weight_unit": "KG",
                        "price": 100.99,
                        "fish_id": 1,
                        "fish_variant_id": 2,
                        "is_SP": False,
                        "is_active": True
                    }
                ],
                "organization_id": 1,
                "user_id": 1,
                "bill_place_id": 1,
                "price": 100.0,
                "discount_id": 1,
                "total_amount": 100.0,
                "billed_amount": 100.0,
                "discounted_price": 90.0,
                "pay_type": 1
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(BillCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        try:
            with transaction.atomic():
                errors, bill = self.controller.create_bill(
                    organization_id=data.organization_id or user.organization.id,
                    user_id=data.user_id or user.id,
                    bill_place_id=data.bill_place_id or user.place.id,
                    price=data.price,
                    discount_id=data.discount_id,
                    total_amount=data.total_amount,
                    billed_amount=data.billed_amount,
                    discounted_price=data.discounted_price,
                    pay_type=data.pay_type,
                    is_active=data.is_active
                )
                if errors:
                    return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

                errors, bill_items = self.bill_item_controller.create_bulk_bill_items(
                    bill_id=bill.id,
                    bill_items=data.bill_items)
                if errors:
                    raise Exception(errors)

                for item in data.bill_items:
                    errors, stock = self.stock_controller.update_stock_weight(
                        place_id=data.bill_place_id or user.place.id,
                        fish_id=item.fish_id,
                        fish_variant_id=item.fish_variant_id,
                        is_SP=item.is_SP,
                        weight=-abs(item.weight),
                        weight_unit=item.weight_unit,
                    )
                    if errors:
                        raise Exception(errors)

                data = {
                    "bill_id": bill.pk,
                    "stock_id": stock.pk,
                    "bill_items": self.bill_item_controller.serialize_queryset(bill_items, self.bill_item_serializer)
                }
                return JsonResponse(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse(data=get_serialized_exception(e)[0], status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Update an existing bill.",
        request=BillEditReqSchema,
        examples=[
            OpenApiExample('Bill Edit Request JSON', value={
                "organization_id": 1,
                "user_id": 1,
                "bill_place_id": 1,
                "price": 150.0,
                "discount_id": 1,
                "total_amount": 150.0,
                "billed_amount": 150.0,
                "discounted_price": 135.0,
                "pay_type": 1
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(BillEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        bill = self.controller.get_instance_by_pk(pk=pk)
        if not bill:
            return JsonResponse({"error": "Bill with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, bill = self.controller.edit_bill(
            bill=bill,
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id or user.id,
            bill_place_id=data.bill_place_id or user.place.id,
            price=data.price,
            discount_id=data.discount_id,
            total_amount=data.total_amount,
            billed_amount=data.billed_amount,
            discounted_price=data.discounted_price,
            pay_type=data.pay_type,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": bill.pk,
            "message": "Bill updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="List all bills.",
        parameters=[
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='organization_id'),
            OpenApiParameter(name='user_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='user_id'),
            OpenApiParameter(name='bill_place_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='bill_place_id'),
            OpenApiParameter(name='discount_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='discount_id'),
            OpenApiParameter(name='pay_type', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='pay_type'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Is Active'),
            OpenApiParameter(name='start_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Start time for filtering'),
            OpenApiParameter(name='end_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='End Time for filtering')
        ],
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(BillListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        cache_key = build_cache_key(
            CacheKeys.BILL_LIST,
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id,
            bill_place_id=data.bill_place_id,
            discount_id=data.discount_id,
            pay_type=data.pay_type,
            is_active=data.is_active,
            start_time=data.start_time,
            end_time=data.end_time,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None  # Remove this line to enable caching
        if instance:
            res = instance
        else:
            errors, data = self.controller.filter_bills(
                organization_id=data.organization_id or user.organization.id,
                user_id=data.user_id,
                bill_place_id=data.bill_place_id,
                discount_id=data.discount_id,
                pay_type=data.pay_type,
                is_active=data.is_active,
                start_time=data.get_start_time(),
                end_time=data.get_end_time(),
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(data, request)
            if page is None:
                page = data

            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="Retrieve a specific Bill by ID.",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='Bill ID'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.BILL_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)

            if not obj:
                return JsonResponse({"error": "BILL with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Make a bill inactive",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='BILL ID')
        ]
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
    def bill_items(self, request, pk, *args, **kwargs):
        # Paginate queryset
        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE

        bill = self.controller.get_instance_by_pk(pk=pk)
        if not bill:
            return JsonResponse({"error": "bill with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        errors, data = self.controller.get_bill_items_with_bill(
            bill=bill
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        page = paginator.paginate_queryset(data, request)
        if page is None:
            page = data

        # Serialize data
        data = self.bill_item_controller.serialize_queryset(page, self.bill_item_serializer)
        result = paginator.get_paginated_response(data)
        return result


class BillItemViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = BillItemController()
    serializer = BillItemSerializer

    @extend_schema(
        description="Create a new Bill Item.",
        request=BillItemCreationReqSchema,
        examples=[
            OpenApiExample('Bill Item Creation Request JSON', value={
                "bill_id": 1,
                "weight": 10.5,
                "weight_unit": "KG",
                "price": 100.99,
                "fish_id": 1,
                "fish_variant_id": 2,
                "is_SP": False,
                "is_active": True
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(BillItemCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        errors, bill_item = self.controller.create_bill_item(
            bill_id=data.bill_id,
            weight=data.weight,
            weight_unit=data.weight_unit,
            price=data.price,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            is_SP=data.is_SP,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": bill_item.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Update an existing Bill Item.",
        request=BillItemEditReqSchema,
        examples=[
            OpenApiExample('Bill Item Edit Request JSON', value={
                "bill_id": 1,
                "weight": 15.5,
                "weight_unit": "KG",
                "price": 150.99,
                "fish_id": 1,
                "fish_variant_id": 3,
                "is_SP": True,
                "is_active": True
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(BillItemEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        bill_item = self.controller.get_instance_by_pk(pk=pk)
        if not bill_item:
            return JsonResponse({"error": "bill item with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)

        errors, bill_item = self.controller.edit_bill_item(
            bill_item=bill_item,
            bill_id=data.bill_id,
            weight=data.weight,
            weight_unit=data.weight_unit,
            price=data.price,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            is_SP=data.is_SP,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": bill_item.pk,
            "message": "Bill Item updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Filter and list bill items",
        parameters=[
            OpenApiParameter(name='bill_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='ID of the bill'),
            OpenApiParameter(name='fish_variant_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='ID of the fish variant'),
            OpenApiParameter(name='is_SP', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='SP status of the bill item'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Active status of the bill item'),
        ],
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(BillItemListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user

        cache_key = build_cache_key(
            CacheKeys.BILL_ITEM_LIST,
            bill_id=data.bill_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            is_SP=data.is_SP,
            is_active=data.is_active,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None
        if instance:
            res = instance
        else:
            errors, data = self.controller.filter_bill_items(
                bill_id=data.bill_id,
                fish_id=data.fish_id,
                fish_variant_id=data.fish_variant_id,
                is_SP=data.is_SP,
                is_active=data.is_active,
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(data, request)
            if page is None:
                page = data

            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=600)  # 10 minutes cache timeout

        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="""
            Serves GET requests for a particular Bill Item by ID.
            GET /api/bill_items/<pk>
            :param request:
            :param pk: Primary Key for bill item entity as path parameter
            :param kwargs:
            :return:
            """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        """
        Serves GET requests for a particular Bill Item by ID.
        GET /api/bill_items/<pk>
        :param request:
        :param pk: Primary Key for bill item entity as path parameter
        :param kwargs:
        :return:
        """
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.BILL_ITEM_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None  # Comment or remove this line if you want to use caching
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return JsonResponse({"error": "Bill Item with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=600)  # 10 minutes cache timeout
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    @extend_schema(
        description="""
            Serves POST requests to make a Bill Item inactive.
            POST /api/bill_items/<id>/make-inactive/
            :param request:
            :param pk:
            :param args:
            :param kwargs:
            :return:
            """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def make_inactive(self, request, pk, *args, **kwargs):
        """
        Serves POST requests to make a Bill Item inactive.
        POST /api/bill_items/<id>/make-inactive/
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


class StockViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = StockController()
    serializer = StockSerializer

    @extend_schema(
        description="Create a new stock entry.",
        request=StockCreationReqSchema,
        examples=[
            OpenApiExample('Stock Creation Request JSON', value={
                "place_id": 1,
                "fish_id": 1,
                "fish_variant_id": 1,
                "is_SP": False,
                "weight": 10.0,
                "weight_unit": "kg"
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(StockCreationReqSchema, request.data)
        if errors:
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        errors, stock = self.controller.create_stock(
            place_id=data.place_id or user.place_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            is_SP=data.is_SP,
            weight=data.weight,
            weight_unit=data.weight_unit
        )
        if errors:
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": stock.pk,
        }
        return Response(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Update an existing stock entry.",
        request=StockEditReqSchema,
        examples=[
            OpenApiExample('Stock Edit Request JSON', value={
                "place_id": 2,
                "fish_variant_id": 2,
                "is_SP": True,
                "weight": 20.0,
                "weight_unit": "kg",
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(StockEditReqSchema, request.data)
        if errors:
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

        stock = self.controller.get_instance_by_pk(pk=pk)
        if not stock:
            return JsonResponse({"error": "stock with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, stock = self.controller.edit_stock(
            stock=stock,
            place_id=data.place_id or user.place_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            is_SP=data.is_SP,
            weight=data.weight,
            weight_unit=data.weight_unit
        )
        if errors:
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": stock.pk,
            "message": "Stock entry updated"
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="List all stock entries.",
        parameters=[
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='organization_id'),
            OpenApiParameter(name='place_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='place_id'),
            OpenApiParameter(name='fish_variant_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='fish_variant_id'),
            OpenApiParameter(name='is_SP', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='is_SP'),
        ],
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(StockListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user

        cache_key = build_cache_key(
            CacheKeys.STOCK_LIST,
            organization_id=data.organization_id or user.organization.id,
            place_id=data.place_id,
            fish_id=data.fish_id,
            fish_variant_id=data.fish_variant_id,
            is_SP=data.is_SP,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None
        if instance:
            res = instance
        else:
            errors, data = self.controller.filter_stocks(
                organization_id=data.organization_id or user.organization.id,
                place_id=data.place_id,
                fish_id=data.fish_id,
                fish_variant_id=data.fish_variant_id,
                is_SP=data.is_SP,
                ordering=data.ordering,
            )
            if errors:
                return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(data, request)
            if page is None:
                page = data

            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)

        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="Retrieve a particular stock entry by ID.",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.STOCK_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return Response({"error": "Stock entry with this ID does not exist"},
                                status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return Response(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Serves POST requests to mark a particular stock as inactive.",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
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


class ExpenseViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = ExpenseController()
    serializer = ExpenseSerializer

    @extend_schema(
        description="Create a new expense.",
        request=ExpenseCreationReqSchema,
        examples=[
            OpenApiExample('Expense Creation Request JSON', value={
                "organization_id": 1,
                "expense_date": "2023-11-01T16:33:34Z",
                "user_id": 1,
                "type_id": 1,
                "desc": "Lunch expense",
                "amount": 15.99
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(ExpenseCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        errors, expense = self.controller.create_expense(
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id or user.id,
            expense_date=data.expense_date,
            type_id=data.type_id,
            desc=data.desc,
            amount=data.amount
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": expense.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Update an existing expense.",
        request=ExpenseEditReqSchema,
        examples=[
            OpenApiExample('Expense Edit Request JSON', value={
                "organization_id": 1,
                "expense_date": "2023-11-01T16:33:34Z",
                "user_id": 1,
                "type_id": 1,
                "desc": "Dinner expense",
                "amount": 20.99
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(ExpenseEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        expense = self.controller.get_instance_by_pk(pk=pk)
        if not expense:
            return JsonResponse({"error": "expense with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, expense = self.controller.edit_expense(
            expense=expense,
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id or user.id,
            expense_date=data.expense_date,
            type_id=data.type_id,
            desc=data.desc,
            amount=data.amount
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": expense.pk,
            "message": "Expense updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="List all expenses.",
        parameters=[
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='organization_id'),
            OpenApiParameter(name='user_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='user_id'),
            OpenApiParameter(name='type_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='type_id'),
            OpenApiParameter(name='desc', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='desc'),
            OpenApiParameter(name='start_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Start time for filtering'),
            OpenApiParameter(name='end_time', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='End Time for filtering')
        ],
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(ExpenseListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user

        cache_key = build_cache_key(
            CacheKeys.EXPENSE_LIST,
            organization_id=data.organization_id or user.organization.id,
            user_id=data.user_id,
            type_id=data.type_id,
            desc=data.desc,
            start_time=data.start_time,
            end_time=data.end_time,
            ordering=data.ordering,
            is_active=data.is_active,
            page=page_key,
            locale=locale,
        )
        instance = cache.get(cache_key)
        instance = None
        if instance:
            res = instance
        else:
            errors, data = self.controller.filter_expenses(
                organization_id=data.organization_id or user.organization.id,
                user_id=data.user_id,
                type_id=data.type_id,
                desc=data.desc,
                start_time=data.get_start_time(),
                end_time=data.get_end_time(),
                ordering=data.ordering,
                is_active=data.is_active
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(data, request)
            if page is None:
                page = data

            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=600)  # 10 minutes cache timeout

        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="""
            Serves GET requests for a particular expense by ID.
            GET /api/expenses/<pk>
            :param request:
            :param pk: Primary Key for expense entity as path parameter
            :param kwargs:
            :return:
            """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        """
        Serves GET requests for a particular expense by ID.
        GET /api/expenses/<pk>
        :param request:
        :param pk: Primary Key for expense entity as path parameter
        :param kwargs:
        :return:
        """
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.EXPENSE_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None  # Comment or remove this line if you want to use caching
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return JsonResponse({"error": "Expense with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=600)  # 10 minutes cache timeout
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    @extend_schema(
        description="""
            Serves POST requests to make an expense inactive.
            POST /api/expenses/<id>/make-inactive/
            :param request:
            :param pk:
            :param args:
            :param kwargs:
            :return:
            """,
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def make_inactive(self, request, pk, *args, **kwargs):
        """
        Serves POST requests to make an expense inactive.
        POST /api/expenses/<id>/make-inactive/
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
