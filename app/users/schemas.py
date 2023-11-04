from typing import Optional, List

from pydantic import BaseModel, validator, EmailStr

from app.users.enums import Designation
from app.utils.helpers import trim_mobile_no, allow_string_rep_of_enum, mobile_number_validation_check
from app.utils.schemas import BaseSchemaCreationReqSchema, BaseSchemaEditReqSchema, BaseSchemaListingReqSchema


def check_mobile_no(mobile_no):
    mobile_no_valid = mobile_number_validation_check(mobile_no)
    if mobile_no_valid is not None:
        raise ValueError(f'Invalid mobile no: {mobile_no}.')
    return mobile_no


class UserCreationReqSchema(BaseSchemaCreationReqSchema):
    name: str
    mobile_no: str
    email: Optional[EmailStr] = ''
    designation: Designation = Designation.NOT_ASSIGNED
    organization_id: Optional[int]
    place_id: Optional[int]
    app_version_code: Optional[int]
    # validator to trim  display number
    _validate_mobile_no = validator('mobile_no',
                                    allow_reuse=True,
                                    pre=True)(trim_mobile_no)

    # Validator to allow string version of enum value too
    _validate_designation = validator('designation',
                                      allow_reuse=True,
                                      pre=True)(allow_string_rep_of_enum)

    # @validator('mobile_no', pre=True, always=True)
    # def validate_type(cls, value):
    #     return check_mobile_no(value)


class UserEditReqSchema(BaseSchemaEditReqSchema):
    name: str
    mobile_no: str
    email: Optional[EmailStr] = ''
    designation: Optional[Designation]
    organization_id: Optional[int]
    place_id: Optional[int]
    app_version_code: Optional[int]
    # validator to trim  display number
    _validate_mobile_no = validator('mobile_no',
                                    allow_reuse=True,
                                    pre=True)(trim_mobile_no)

    # Validator to allow string version of enum value too
    _validate_designation = validator('designation',
                                      allow_reuse=True,
                                      pre=True)(allow_string_rep_of_enum)

    # @validator('mobile_no', pre=True, always=True)
    # def validate_type(cls, value):
    #     return check_mobile_no(value)


class UserListingReqSchema(BaseSchemaListingReqSchema):
    search_query: Optional[str]
    designation: Optional[Designation]
    place_id: Optional[int]
    organization_id: Optional[int]

    # Validator to allow string version of enum value too
    _validate_designation = validator('designation',
                                      allow_reuse=True,
                                      pre=True)(allow_string_rep_of_enum)
