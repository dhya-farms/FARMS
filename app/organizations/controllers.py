from django.db.models import Q
from django.db.utils import IntegrityError

from app.organizations.models import Organization, Place, ExpenseType
from app.organizations.serializers import OrganizationSerializer, PlaceSerializer
from app.utils.controllers import Controller
from app.utils.helpers import get_serialized_exception


class OrganizationController(Controller):
    def __init__(self):
        self.model = Organization

    def create_organization(self, name, logo, address, is_active):
        try:
            organization = self.model.objects.create(
                name=name,
                logo=logo,
                address=address,
                is_active=is_active
            )
            return None, organization
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_organization(self, organization, name, logo, address, is_active):
        try:
            organization.name = name
            organization.logo = logo
            organization.address = address
            organization.is_active = is_active

            organization.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, organization

    def filter_organization(self,
                            name,
                            is_active,
                            ordering):
        organization_qs = self.get_valid_organizations()

        try:
            if is_active:
                organization_qs = organization_qs.filter(is_active=is_active)

            query = Q()
            if name:
                query |= Q(name__icontains=name)

            organization_qs = organization_qs.filter(query)
            ordering = ordering if ordering is not None else '-created_at'
            if ordering:
                organization_qs = organization_qs.order_by(ordering)
            return None, organization_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_organizations(self):
        return self.model.objects.all()


class PlaceController(Controller):
    def __init__(self):
        self.model = Place

    def create_place(self,
                     name,
                     address,
                     mobile_no,
                     type,
                     is_active,
                     organization_id,
                     center_id):
        try:
            place = self.model.objects.create(
                name=name,
                address=address,
                mobile_no=mobile_no,
                type=type,
                is_active=is_active,
                organization_id=organization_id,
                center_id=center_id
            )
            return None, place
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_place(self, place_obj, name, address, mobile_no, type, is_active, organization_id, center_id):
        try:
            place_obj.name = name
            place_obj.address = address
            place_obj.mobile_no = mobile_no
            place_obj.type = type
            place_obj.is_active = is_active
            place_obj.organization_id = organization_id
            place_obj.center_id = center_id

            place_obj.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, place_obj

    def filter_places(self,
                      organization_id,
                      name,
                      type,
                      is_active,
                      center_id,
                      ordering):
        place_qs = self.get_valid_places()

        try:
            if organization_id:
                place_qs = place_qs.filter(organization_id=organization_id)

            if is_active:
                place_qs = place_qs.filter(is_active=is_active)

            if type:
                place_qs = place_qs.filter(type=type)

            if center_id:
                place_qs = place_qs.filter(center_id=center_id)

            query = Q()
            if name:
                query |= Q(name__icontains=name)
            ordering = ordering if ordering is not None else 'name'
            if ordering:
                place_qs = place_qs.order_by(ordering)

            place_qs = place_qs.filter(query)
            return None, place_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_landings_with_center(self, center):
        try:
            landings = center.landings.all()
            return None, landings
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_places(self):
        return self.model.objects.all()


class ExpenseTypeController(Controller):
    def __init__(self):
        self.model = ExpenseType

    def create_expense_type(self, name, is_active, organization_id):
        try:
            expense_type = self.model.objects.create(
                name=name,
                is_active=is_active,
                organization_id=organization_id
            )
            return None, expense_type
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_expense_type(self, expense_type, name, is_active, organization_id):
        try:
            if name:
                expense_type.name = name
            if is_active is not None:
                expense_type.is_active = is_active
            if organization_id:
                expense_type.organization_id = organization_id

            expense_type.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, expense_type

    def filter_expense_types(self,
                             name,
                             is_active,
                             organization_id,
                             ordering):
        expense_type_qs = self.get_valid_expense_types()

        try:
            if is_active is not None:
                expense_type_qs = expense_type_qs.filter(is_active=is_active)
            if organization_id:
                expense_type_qs = expense_type_qs.filter(organization_id=organization_id)
            if name:
                expense_type_qs = expense_type_qs.filter(name__icontains=name)
            ordering = ordering if ordering is not None else '-created_at'
            if ordering:
                expense_type_qs = expense_type_qs.order_by(ordering)
            return None, expense_type_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_expense_types(self):
        return self.model.objects.all()
