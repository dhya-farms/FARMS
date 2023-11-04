from typing import Optional, List

from pydantic import BaseModel, validator, EmailStr, condecimal, conint

from app.organizations.enums import PlaceType
from app.utils.helpers import allow_string_rep_of_enum
from app.utils.schemas import BaseSchemaCreationReqSchema, BaseSchemaEditReqSchema, BaseSchemaListingReqSchema


class OrganizationCreationReqSchema(BaseSchemaCreationReqSchema):
    name: str
    logo: Optional[str] = None
    address: Optional[str] = None


class OrganizationEditReqSchema(BaseSchemaEditReqSchema):
    name: str
    logo: Optional[str] = None
    address: Optional[str] = None


class OrganizationListingReqSchema(BaseSchemaListingReqSchema):
    name: Optional[str]


class PlaceCreationReqSchema(BaseSchemaCreationReqSchema):
    name: str
    address: Optional[str]
    mobile_no: Optional[str]
    type: PlaceType
    organization_id: Optional[int]
    center_id: Optional[int]

    # Validator to allow string version of enum value too
    _validate_type = validator('type',
                               allow_reuse=True,
                               pre=True)(allow_string_rep_of_enum)


class PlaceEditReqSchema(BaseSchemaEditReqSchema):
    name: str
    address: Optional[str]
    mobile_no: Optional[str]
    type: PlaceType
    organization_id: Optional[int]
    center_id: Optional[int]

    # Validator to allow string version of enum value too
    _validate_type = validator('type',
                               allow_reuse=True,
                               pre=True)(allow_string_rep_of_enum)


class PlaceListingReqSchema(BaseSchemaListingReqSchema):
    organization_id: Optional[int]
    name: Optional[str]
    type: Optional[PlaceType]
    center_id: Optional[int]

    # Validator to allow string version of enum value too
    _validate_type = validator('type',
                               allow_reuse=True,
                               pre=True)(allow_string_rep_of_enum)


class ExpenseTypeCreationReqSchema(BaseSchemaCreationReqSchema):
    name: str
    organization_id: Optional[int]


class ExpenseTypeEditReqSchema(BaseSchemaEditReqSchema):
    name: Optional[str]
    organization_id: Optional[int]


class ExpenseTypeListingReqSchema(BaseSchemaListingReqSchema):
    name: Optional[str]
    organization_id: Optional[int]
