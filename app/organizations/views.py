from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from app.organizations.controllers import OrganizationController, PlaceController, \
    ExpenseTypeController
from app.organizations.schemas import OrganizationCreationReqSchema, OrganizationEditReqSchema, \
    OrganizationListingReqSchema, PlaceCreationReqSchema, PlaceEditReqSchema, PlaceListingReqSchema, \
    ExpenseTypeCreationReqSchema, ExpenseTypeEditReqSchema, ExpenseTypeListingReqSchema
from app.organizations.serializers import OrganizationSerializer, PlaceSerializer, ExpenseTypeSerializer
from app.utils.authentication import IsOrganizationUser
from app.utils.constants import Timeouts, CacheKeys
from app.utils.helpers import build_cache_key, qdict_to_dict


class OrganizationViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = OrganizationController()
    serializer = OrganizationSerializer

    @extend_schema(
        description="Serves POST requests for creating an Organization",
        request=OrganizationCreationReqSchema,
        examples=[
            OpenApiExample('Organization Creation Request JSON', value={
                "name": "Sample Organization",
                "logo": "organization_logo_url",
                "address": "Organization Address",
                "is_active": True
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(OrganizationCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        errors, organization = self.controller.create_organization(
            name=data.name,
            logo=data.logo,
            address=data.address,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": organization.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Partially updates an existing organization",
        request=OrganizationEditReqSchema,
        examples=[
            OpenApiExample('Organization Edit Request JSON', value={
                "name": "Updated Organization",
                "logo": "updated_logo_url",
                "address": "Updated Address",
                "is_active": False
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(OrganizationEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        organization = self.controller.get_instance_by_pk(pk=pk)
        if not organization:
            return JsonResponse({"error": "organization with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)

        errors, organization = self.controller.edit_organization(
            organization=organization,
            name=data.name,
            logo=data.logo,
            address=data.address,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": organization.pk,
            "message": "Organization profile updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Filter and list organizations",
        parameters=[
            OpenApiParameter(name='name', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Name of the organization'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Active status of the organization'),
        ],
    )
    def list(self, request, **kwargs):
        """
       Serves GET requests given on the entity API root path.
       GET /api/places/
       :param request:
       :param kwargs:
       :return:
       """
        errors, data = self.controller.parse_request(OrganizationListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        # Paginate queryset
        paginator = PageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE

        cache_key = build_cache_key(
            CacheKeys.ORGANIZATION_LIST,
            name=data.name,
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
            errors, organizations = self.controller.filter_organization(
                name=data.name,
                is_active=data.is_active,
                ordering=data.ordering,
            )

            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(organizations, request)
            if page is None:
                page = data

            # Serialize data
            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="Retrieve a specific organization by ID",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int,
                             description='ID of the organization'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        """
       Serves GET requests coming for a particular entity by id `pk`
       GET /api/organizations/<pk>
       :param request:
       :param pk: Primary Key for organization entity as path parameter
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
                return JsonResponse({"error": "Organization with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves POST requests coming for a particular entity by id `pk`
        POST /api/organizations/<pk>/make_inactive
        :param request:
        :param pk: Primary Key for organization entity as path parameter
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
        """
               Serves POST requests coming for a particular entity by id `pk`
               POST /api/fish/<pk>/make_inactive
               :param request:
               :param pk: Primary Key for user entity as path parameter
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


class PlaceViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = PlaceController()
    serializer = PlaceSerializer

    @extend_schema(
        description="Create a new place",
        request=PlaceCreationReqSchema,
        examples=[
            OpenApiExample('Place Creation Request JSON', value={
                "name": "Sample Place",
                "address": "16 A",
                "mobile_no": "9344015965",
                "organization_id": 1,
                "is_active": True,
                "type": 1,
                "center_id": 3
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(PlaceCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        errors, place = self.controller.create_place(
            name=data.name,
            address=data.address,
            mobile_no=data.mobile_no,
            type=data.type,
            is_active=data.is_active,
            organization_id=data.organization_id or user.organization.id,
            center_id=data.center_id
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": place.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Edit an existing place",
        request=PlaceEditReqSchema,
        examples=[
            OpenApiExample('Place Edit Request JSON', value={
                "name": "Updated Place",
                "address": "16 A",
                "mobile_no": "9344015965",
                "organization_id": 1,
                "is_active": True,
                "type": 1,
                "center_id": 3

            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(PlaceEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        place_obj = self.controller.get_instance_by_pk(pk=pk)
        if not place_obj:
            return JsonResponse({"error": "Place with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, place_obj = self.controller.edit_place(
            place_obj=place_obj,
            name=data.name,
            address=data.address,
            mobile_no=data.mobile_no,
            type=data.type,
            is_active=data.is_active,
            organization_id=data.organization_id or user.organization.id,
            center_id=data.center_id
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": place_obj.pk,
            "message": "Place profile updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Retrieve a list of places based on filtering criteria",
        parameters=[
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Organization ID'),
            OpenApiParameter(name='name', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Name'),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='Place Type'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='Is Active'),
            OpenApiParameter(name='center_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='Center ID'),
        ]
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(PlaceListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginate queryset
        paginator = PageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        # organization_id = None  # You can set organization_id if required
        cache_key = build_cache_key(
            CacheKeys.PLACE_LIST,
            organization_id=data.organization_id or user.organization.id,
            name=data.name,
            type=data.type,
            is_active=data.is_active,
            center_id=data.center_id,
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
            errors, place_qs = self.controller.filter_places(
                organization_id=data.organization_id or user.organization.id,
                name=data.name,
                type=data.type,
                is_active=data.is_active,
                center_id=data.center_id,
                ordering=data.ordering,
            )
            if errors:
                return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
            page = paginator.paginate_queryset(place_qs, request)
            if page is None:
                page = data

            # Serialize data
            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=Timeouts.MINUTES_10)
        result = paginator.get_paginated_response(res)
        return result

        # Implement filtering and pagination logic as needed

    @extend_schema(
        description="Retrieve a specific place by ID",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='Place ID')
        ]
    )
    def retrieve(self, request, pk, *args, **kwargs):
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.PLACE_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None

        if instance:
            data = instance
        else:
            place_obj = self.controller.get_instance_by_pk(pk=pk)
            if not place_obj:
                return JsonResponse({"error": "Place with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(place_obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)

        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves POST requests coming for a particular entity by id `pk`
        POST /api/places/<pk>/make_inactive
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
    @action(methods=['POST'], detail=True)
    def make_inactive(self, request, pk, *args, **kwargs):
        """
               Serves POST requests coming for a particular entity by id `pk`
               POST /api/places/<pk>/make_inactive
               :param request:
               :param pk: Primary Key for user entity as path parameter
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

    @extend_schema(
        description="""
        Serves POST requests for getting landings under specific center with center 'id'
        POST /api/places/<pk>/landings/
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
    @action(methods=['GET'], detail=True)
    def landings(self, request, pk, *args, **kwargs):
        """
                Serves POST requests for getting landings under specific center with center 'id'
                GET /api/places/<pk>/landings/
                :param request:
                :param pk: Primary Key for user entity as path parameter
                :param kwargs:
                :return:
        """

        # Paginate queryset
        paginator = PageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE

        center = self.controller.get_instance_by_pk(pk=pk)
        if not center:
            return JsonResponse({"error": "center with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        errors, data = self.controller.get_landings_with_center(
            center=center
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        page = paginator.paginate_queryset(data, request)
        if page is None:
            page = data

        # Serialize data
        data = self.controller.serialize_queryset(page, self.serializer)
        result = paginator.get_paginated_response(data)
        return result


class ExpenseTypeViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = ExpenseTypeController()
    serializer = ExpenseTypeSerializer

    @extend_schema(
        description="""
            Serves POST requests for creating a new expense type.
            This endpoint creates an expense type in the database.
            Mainly handles the requests coming from the app.
            """,
        request=ExpenseTypeCreationReqSchema,
        examples=[
            OpenApiExample('Expense Type Creation Request JSON', value={
                "name": "Sample Expense Type",
                "is_active": True,
                "organization_id": 1
            })
        ]
    )
    def create(self, request, *args, **kwargs):
        errors, data = self.controller.parse_request(ExpenseTypeCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        errors, expense_type = self.controller.create_expense_type(
            name=data.name,
            is_active=data.is_active,
            organization_id=data.organization_id or user.organization_id
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": expense_type.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description=""" Partially update an existing expense type.
                """,
        request=ExpenseTypeEditReqSchema,
        examples=[
            OpenApiExample('Expense Type Edit Request JSON', value={
                "name": "Edited Expense Type",
                "is_active": False,
                "organization_id": 1
            })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        errors, data = self.controller.parse_request(ExpenseTypeEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        expense_type = self.controller.get_instance_by_pk(pk=pk)
        if not expense_type:
            return JsonResponse({"error": "expense type with this id does not exists"},
                                status=status.HTTP_404_NOT_FOUND)
        user = request.user
        errors, expense_type = self.controller.edit_expense_type(
            expense_type=expense_type,
            name=data.name,
            is_active=data.is_active,
            organization_id=data.organization_id or user.organization_id
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": expense_type.pk,
            "message": "Expense type updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="List all expense types.",
        parameters=[
            OpenApiParameter(name='name', location=OpenApiParameter.QUERY, required=False, type=str,
                             description='name'),
            OpenApiParameter(name='is_active', location=OpenApiParameter.QUERY, required=False, type=bool,
                             description='is_active'),
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='organization_id'),
        ],
    )
    def list(self, request, **kwargs):
        errors, data = self.controller.parse_request(ExpenseTypeListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = PageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user

        cache_key = build_cache_key(
            CacheKeys.EXPENSE_TYPE_LIST,
            name=data.name,
            organization_id=data.organization_id or user.organization.id,
            is_active=data.is_active,
            ordering=data.ordering,
            page=page_key,
            locale=locale
        )
        instance = cache.get(cache_key)
        instance = None  # Comment or remove this line if you want to use caching
        if instance:
            res = instance
        else:
            errors, data = self.controller.filter_expense_types(
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

            data = self.controller.serialize_queryset(page, self.serializer)
            res = data
            cache.set(cache_key, res, timeout=600)  # 10 minutes cache timeout

        result = paginator.get_paginated_response(res)
        return result

    @extend_schema(
        description="Serves GET requests for a particular expense type by ID.",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    def retrieve(self, request, pk, *args, **kwargs):
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.EXPENSE_TYPE_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None  # Comment or remove this line if you want to use caching
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return JsonResponse({"error": "Expense type with this ID does not exist"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=600)  # 10 minutes cache timeout
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Serves POST requests to make an expense type inactive.",
        parameters=[
            OpenApiParameter(name='pk', location=OpenApiParameter.PATH, required=True, type=int, description='pk'),
        ],
    )
    @action(methods=['POST'], detail=True)
    def make_inactive(self, request, pk, *args, **kwargs):
        """
                Serves POST requests to make an expense type inactive.
                POST /api/expense_types/<id>/make-inactive/
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
