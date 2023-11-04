from django.conf import settings
from django.db import IntegrityError
from django.utils import translation
from pydantic import ValidationError
from app.utils.helpers import get_serialized_exception
from app.utils.schemas import BaseSchemaListingReqSchema


class Controller:
    def parse_request(self, request_schema, data):
        try:
            parsed_request = request_schema(**data)
            if issubclass(request_schema, BaseSchemaListingReqSchema):
                parsed_request.get_start_time()
                parsed_request.get_end_time()
            return None, parsed_request
        except (ValidationError, ValueError) as e:  # Catch both Pydantic's ValidationError and ValueError
            # The error messages can be combined or handled separately as needed
            return {"errors": e.errors() if isinstance(e, ValidationError) else str(e)}, None

    def get_instance_by_pk(self, pk: int):
        try:
            instance = self.model.objects.get(pk=pk)
            return instance
        except self.model.DoesNotExist as e:
            return None

    def serialize_one(self, obj, serializer_override=None):
        serializer_class = serializer_override

        data = serializer_class(obj).data
        return data

    def serialize_queryset(self, obj_list, serializer_override=None):
        data = []
        for obj in obj_list:
            data.append(self.serialize_one(obj, serializer_override))
        return data

    def make_inactive(self, obj):
        try:
            obj.is_active = False
            obj.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, True


