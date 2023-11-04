from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Q, Case, When, Value, Count
from django.utils import timezone
from django.utils import translation
from django.db import IntegrityError

from app.users.enums import Designation
from app.users.models import User
from app.users.serializers import UserSerializer
from app.utils.controllers import Controller
from app.utils.helpers import generate_random_username, get_serialized_exception


class UserController(Controller):
    def __init__(self):
        self.model = get_user_model()

    def create_user(self,
                    name,
                    email,
                    mobile_no,
                    designation,
                    organization_id,
                    place_id,
                    app_version_code,
                    is_active):
        """
        take attributes of user including designation and create user model in DB

        :param is_active:
        :param name:
        :param email:
        :param mobile_no:
        :param designation:
        :param organization_id:
        :param place_id:
        :param app_version_code:
        """
        try:
            user = self.model.objects.create(
                username=generate_random_username(),
                name=name,
                email=email,
                mobile_no=mobile_no,
                designation=designation,
                organization_id=organization_id,
                place_id=place_id,
                app_version_code=app_version_code,
                is_active=is_active
            )
            return None, user
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_user(self,
                  user,
                  name,
                  email,
                  mobile_no,
                  designation,
                  organization_id,
                  place_id,
                  app_version_code,
                  is_active):
        """
        Update user model using the attributes specified
        :param is_active:
        :param user:
        :param name:
        :param email:
        :param mobile_no:
        :param designation:
        :param organization_id:
        :param place_id:
        :param app_version_code:
        """
        # if user.designation != designation:
        #     # TODO
        #     return {'errors': 'User type change is not possible.'}, None
        try:
            user.name = name
            user.email = email
            user.mobile_no = mobile_no
            user.designation = designation
            user.organization_id = organization_id
            user.place_id = place_id
            user.app_version_code = app_version_code
            user.is_active = is_active

            user.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, user

    def filter_user(self,
                    search_queries,
                    designation,
                    place_id,
                    organization_id,
                    is_active,
                    ordering
                    ):
        user_qs = self.get_valid_users()

        try:

            if is_active:
                user_qs = user_qs.filter(is_active=is_active)

            if organization_id:
                user_qs = user_qs.filter(organization_id=organization_id)

            if designation:
                user_qs = user_qs.filter(designation=designation)

            if place_id:
                user_qs = user_qs.filter(place_id=place_id)

            # Initialize an empty Q object to start the filter.
            query = Q()

            # Add conditions for name, mobile_no, and email based on the search query.
            if search_queries:
                query |= Q(name__icontains=search_queries) | Q(mobile_no__contains=search_queries) | Q(
                        email__contains=search_queries)

            user_qs = user_qs.filter(query)
            ordering = ordering if ordering is not None else '-date_joined'
            if ordering:
                user_qs = user_qs.order_by(ordering)
            return None, user_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_users(self):
        return self.model.objects.all()
