import random

from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from app.users.controllers import UserController
from app.users.enums import Designation
from app.users.schemas import UserCreationReqSchema, UserEditReqSchema, UserListingReqSchema
from app.users.serializers import UserSerializer
# from app.users.tasks import send_otp
from app.utils.authentication import IsOrganizationAdminUser, IsOrganizationUser
from app.utils.constants import Timeouts, CacheKeys, SMS
from app.utils.helpers import mobile_number_validation_check, qdict_to_dict, \
    generate_random_username, build_cache_key

User = get_user_model()


class OtpLoginViewSet(viewsets.ViewSet):

    @extend_schema(
        description="Generates OTP for the provided mobile number and sends it via SMS.",
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample('Example JSON', value={"mobile_no": "1234567890"})
        ]
    )
    @action(methods=["POST"], detail=False)
    def generate(self, request):
        # this api does not need auth token
        # Generate otp, store it in cache, send sms using yellow.ai
        # request_body : {"mobile_no"}

        mobile_no = request.data.get('mobile_no', None)
        mobile_no_valid = mobile_number_validation_check(mobile_no)
        if mobile_no_valid is not None:
            return Response(data={"message": mobile_no_valid}, status=status.HTTP_400_BAD_REQUEST)

        mobile_no = str(mobile_no)

        static_otp_mobile_numbers = ['9344015965', '8971165979', '7013991532', '9959727836', '1414141414',
                                     '8858327030']  # can keep the numbers in .env file
        if mobile_no in static_otp_mobile_numbers:
            otp = "1111"
        else:
            otp = str(random.randint(1000, 9999))
        if settings.DEBUG:
            otp = "1111"
        cache.set("otp_" + mobile_no, otp, timeout=300)
        message = SMS.OTP_LOGIN.format(otp=otp)
        # send_otp(mobile_no=mobile_no, message=message)
        # send_otp.apply_async(
        #     kwargs={'mobile_no': mobile_no, 'message': message})
        return Response(data={"message": "otp generated"}, status=status.HTTP_200_OK)

    @extend_schema(
        description="Resends the OTP to the provided mobile number.",
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample('Example JSON', value={"mobile_no": "1234567890"})
        ]
    )
    @action(methods=["POST"], detail=False)
    def resend(self, request):
        # request_body : {"mobile_no"}
        mobile_no = request.data.get('mobile_no', None)
        mobile_no_valid = mobile_number_validation_check(mobile_no)
        if mobile_no_valid is not None:
            return Response(data={"message": mobile_no_valid}, status=status.HTTP_400_BAD_REQUEST)
        mobile_no = str(mobile_no)
        otp = cache.get("otp_" + mobile_no)
        if otp:
            cache.set("otp_" + mobile_no, otp, timeout=300)
            # message = GupshupSMSIntegration.OTP_SMS.replace("{otp}", str(otp))
            # send_sms_to_user.delay(mobile_no=mobile_no, message=message)
            return Response(data={"message": "resent otp"}, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "OTP not sent or it is expired"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Verifies the provided OTP and logs in the user.",
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample('Example JSON', value={"mobile_no": "1234567890", "otp": "1234"})
        ]
    )
    @action(methods=["POST"], detail=False)
    def verify(self, request):
        # this api does not need auth token
        # request_body : {"otp", "mobile_no"}

        mobile_no = request.data.get('mobile_no', None)
        mobile_no_valid = mobile_number_validation_check(mobile_no)
        if mobile_no_valid is not None:
            return Response(data={"message": mobile_no_valid}, status=status.HTTP_400_BAD_REQUEST)
        mobile_no = str(mobile_no)
        otp = str(request.data.get("otp"))
        otp_from_cache = cache.get("otp_" + mobile_no)
        if otp_from_cache is None:
            return Response(data={"message": "OTP not sent or it is expired"},
                            status=status.HTTP_400_BAD_REQUEST)
        if otp != otp_from_cache:
            return Response(data={"message": "Incorrect otp"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cache.delete("otp_" + mobile_no)
            user = User.objects.filter(mobile_no=mobile_no).select_related('auth_token').order_by('-id').first()
            if user is None:
                user = User.objects.create(username=generate_random_username(), designation=Designation.NOT_ASSIGNED)
                user.mobile_no = mobile_no
                token, created = Token.objects.get_or_create(user=user)
                user.auth_token = token
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            print(request.user)
            user.last_login = timezone.now()
            user.save()
            auth_token = user.auth_token
            response = Response(data={
                "message": "successfully logged in",
                "user_id": user.id,
                "token": auth_token.key},
                status=status.HTTP_200_OK)
            return response

    @extend_schema(
        description="Logs out the authenticated user.",
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(methods=["POST"], detail=False)
    def logout(self, request):
        # Get the token associated with the user and delete it
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass  # No token found for user

        logout(request)
        response = Response(data={"message": "successfully logged out"},
                            status=status.HTTP_200_OK)
        return response


class AuthenticationViewSet(viewsets.ViewSet):

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        custom_permission_classes = []
        if self.action == 'login':
            custom_permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in custom_permission_classes]

    @extend_schema(
        description="logs in the user and provide the user type and token.",
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample('Example JSON', value={"mobile_no": "1234567890"})
        ]
    )
    @action(methods=["POST"], detail=False)
    def login(self, request):
        # this api does not need auth token
        # request_body : {"otp", "mobile_no"}

        mobile_no = request.data.get('mobile_no', None)
        mobile_no_valid = mobile_number_validation_check(mobile_no)
        if mobile_no_valid is not None:
            return Response(data={"message": mobile_no_valid}, status=status.HTTP_400_BAD_REQUEST)
        mobile_no = str(mobile_no)

        user = User.objects.filter(mobile_no=mobile_no).select_related('auth_token').order_by('-id').first()
        if user is None:
            user = User.objects.create(username=generate_random_username(), designation=Designation.NOT_ASSIGNED)
            user.mobile_no = mobile_no
            token, created = Token.objects.get_or_create(user=user)
            user.auth_token = token
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(request.user)
        user.last_login = timezone.now()
        user.save()
        auth_token = user.auth_token
        response = Response(data={
            "message": "successfully logged in",
            "user_id": user.id,
            "token": auth_token.key,
            "designation": str(Designation(user.designation).name)},
            status=status.HTTP_200_OK)
        return response

    @extend_schema(
        description="Logs out the authenticated user.",
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(methods=["POST"], detail=False)
    def logout(self, request):
        # Get the token associated with the user and delete it
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass  # No token found for user

        logout(request)
        response = Response(data={"message": "successfully logged out"},
                            status=status.HTTP_200_OK)
        return response


class UserViewSet(viewsets.ViewSet):
    permission_classes = (IsOrganizationUser,)
    controller = UserController()
    serializer = UserSerializer

    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     if self.action == 'create':
    #         custom_permission_classes = [IsOrganizationAdminUser]
    #     else:
    #         custom_permission_classes = [IsAuthenticated]
    #     return [permission() for permission in custom_permission_classes]

    @extend_schema(
        description="""
        Serves POST requests given on the entity API root path for user object creation
        This creates User Row in database and Mainly handles the requests coming from app
        """,
        request=UserCreationReqSchema,
        examples=[
            OpenApiExample('Example JSON', value={"name": "John Doe",
                                                  "mobile_no": "1234567890",
                                                  "email": "johndoe@example.com",
                                                  "designation": 1,
                                                  "organization_id": 1,
                                                  "place_id": 2,
                                                  "app_version_code": 3
                                                  })
        ]
    )
    def create(self, request, *args, **kwargs):
        """
        Serves POST requests given on the entity API root path for user object creation
        This creates user Row in database and also corresponding subclass's row too
        Mainly handles the requests coming from app

        POST /api/users/
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(UserCreationReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Create User
        errors, user = self.controller.create_user(
            name=data.name,
            email=data.email,
            mobile_no=data.mobile_no,
            designation=data.designation,
            organization_id=data.organization_id,
            place_id=data.place_id,
            app_version_code=data.app_version_code,
            is_active=data.is_active
        )
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": user.pk,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description=""" Partial updates the existing user
            """,
        request=UserEditReqSchema,
        examples=[
            OpenApiExample('Example JSON', value={"name": "John Doe",
                                                  "mobile_no": "1234567890",
                                                  "email": "johndoe@example.com",
                                                  "designation": 1,
                                                  "organization_id": 1,
                                                  "place_id": 2,
                                                  "app_version_code": 3
                                                  })
        ]
    )
    def partial_update(self, request, pk, *args, **kwargs):
        # Parsing request
        errors, data = self.controller.parse_request(UserEditReqSchema, request.data)
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract previous user object
        user = self.controller.get_instance_by_pk(pk=pk)

        # Update User
        errors, user = self.controller.edit_user(
            user=user,
            name=data.name,
            email=data.email,
            mobile_no=data.mobile_no,
            designation=data.designation,
            organization_id=data.organization_id,
            place_id=data.place_id,
            app_version_code=data.app_version_code,
            is_active=data.is_active
        )

        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "id": user.pk,
            "message": "user profile updated"
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves GET requests given on the entity API root path.
        GET /api/users/
        :param request:
        :param kwargs:
        :return:
        """,
        parameters=[
            OpenApiParameter(name='designation', location=OpenApiParameter.QUERY, required=False,
                             type=int,
                             description='fish_transaction_type'),
            OpenApiParameter(name='place_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='place_id'),
            OpenApiParameter(name='organization_id', location=OpenApiParameter.QUERY, required=False, type=int,
                             description='organization_id'),
        ],
    )
    def list(self, request, **kwargs):
        """
        Serves GET requests given on the entity API root path.
        GET /api/users/
        :param request:
        :param kwargs:
        :return:
        """
        # Parsing request
        errors, data = self.controller.parse_request(UserListingReqSchema, qdict_to_dict(request.query_params))
        if errors:
            return JsonResponse(data=errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginate queryset
        paginator = PageNumberPagination()
        page_key = request.query_params.get('page')
        locale = request.LANGUAGE_CODE
        user = request.user
        cache_key = build_cache_key(
            CacheKeys.USER_LIST,
            search_queries=data.search_query,
            organization_id=data.organization_id or user.organization.id,
            designation=data.designation,
            place_id=data.place_id,
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
            errors, data = self.controller.filter_user(
                search_queries=data.search_query,
                designation=data.designation,
                place_id=data.place_id,
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
        GET /api/users/<pk>
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
        GET /api/users/<pk>
        :param request:
        :param pk: Primary Key for user entity as path parameter
        :param kwargs:
        :return:
        """
        locale = request.LANGUAGE_CODE
        cache_key = CacheKeys.USER_DETAILS_BY_PK.value.format(pk=pk, locale=locale)
        instance = cache.get(cache_key)
        instance = None
        if instance:
            data = instance
        else:
            obj = self.controller.get_instance_by_pk(pk=pk)
            if not obj:
                return JsonResponse({"error": "user with this id does not exists"},
                                    status=status.HTTP_404_NOT_FOUND)
            data = self.controller.serialize_one(obj, self.serializer)
            cache.set(cache_key, data, timeout=Timeouts.MINUTES_10)
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @extend_schema(
        description="""
        Serves POST requests coming for a particular entity by id `pk`
        POST /api/users/<pk>/make_inactive
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
        POST /api/users/<pk>/make_inactive
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