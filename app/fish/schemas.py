from datetime import datetime
from typing import Optional, List

from decimal import Decimal
from pydantic import BaseModel, validator, condecimal, conint

from app.fish.enums import WeightUnit
from app.organizations.enums import PlaceType
from app.utils.helpers import convert_to_decimal, allow_string_rep_of_enum
from app.utils.schemas import BaseSchemaCreationReqSchema, BaseSchemaEditReqSchema, BaseSchemaListingReqSchema

MOBILE_NO_LIMIT = 10


def check_sales_place_type(value):
    allowed_types = {PlaceType.MARKET, PlaceType.MERCHANT, PlaceType.RETAIL}
    if value not in allowed_types:
        raise ValueError(f'Invalid type: {value}. Allowed values are {allowed_types}')
    return value


class FishCreationReqSchema(BaseSchemaCreationReqSchema):
    name: str
    organization_id: Optional[int]


class FishEditReqSchema(BaseSchemaEditReqSchema):
    name: str
    organization_id: Optional[int]


class FishListingReqSchema(BaseSchemaListingReqSchema):
    name: Optional[str]
    organization_id: Optional[int]


class FishVariantCreationReqSchema(BaseSchemaCreationReqSchema):
    fish_id: int
    name: str
    price: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS

    _validate_price = validator('price',
                                allow_reuse=True,
                                pre=True)(convert_to_decimal)


class FishVariantEditReqSchema(BaseSchemaEditReqSchema):
    fish_id: int
    name: str
    price: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS

    _validate_price = validator('price',
                                allow_reuse=True,
                                pre=True)(convert_to_decimal)


class FishVariantListingReqSchema(BaseSchemaListingReqSchema):
    fish_id: Optional[int]
    organization_id: Optional[int]
    name: Optional[str]


class DiscountCreationReqSchema(BaseSchemaCreationReqSchema):
    name: str
    discount: conint(ge=0, le=100) = 0
    type: PlaceType
    organization_id: Optional[int]

    # Validator to allow string version of enum value too
    _validate_type = validator('type',
                               allow_reuse=True,
                               pre=True)(allow_string_rep_of_enum)

    @validator('type', pre=True, allow_reuse=True)
    def validate_type(cls, value):
        return check_sales_place_type(value)


class DiscountEditReqSchema(BaseSchemaEditReqSchema):
    name: str
    discount: conint(ge=0, le=100)
    type: PlaceType
    organization_id: Optional[int]

    # Validator to allow string version of enum value too
    _validate_type = validator('type',
                               allow_reuse=True,
                               pre=True)(allow_string_rep_of_enum)

    @validator('type', pre=True, allow_reuse=True)
    def validate_type(cls, value):
        return check_sales_place_type(value)


class DiscountListingReqSchema(BaseSchemaListingReqSchema):
    organization_id: Optional[int]
    name: Optional[str]
    type: Optional[PlaceType]

    # Validator to allow string version of enum value too
    _validate_type = validator('type',
                               allow_reuse=True,
                               pre=True)(allow_string_rep_of_enum)

    @validator('type', pre=True, allow_reuse=True)
    def validate_type(cls, value):
        return check_sales_place_type(value)


class PriceHistoryListingSchema(BaseSchemaListingReqSchema):
    user_id: Optional[int]
    fish_id: Optional[int]
    fish_variant_id: Optional[int]
