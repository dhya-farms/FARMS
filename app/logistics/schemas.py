from datetime import datetime
from typing import Optional, List

from decimal import Decimal
from pydantic import BaseModel, validator, condecimal, conint

from app.fish.enums import WeightUnit
from app.logistics.enums import PayType, RecordType
from app.utils.helpers import convert_to_decimal, allow_string_rep_of_enum
from app.utils.schemas import BaseSchemaCreationReqSchema, BaseSchemaEditReqSchema, BaseSchemaListingReqSchema


class RecordCreationReqSchema(BaseSchemaCreationReqSchema):
    organization_id: Optional[int]
    user_id: Optional[int]
    import_from_id: Optional[int]
    export_to_id: Optional[int]
    record_type: Optional[RecordType]
    discount_id: Optional[int]
    fish_variant_id: Optional[int]
    weigh_place_id: Optional[int]
    weight: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS
    is_SP: bool = False

    _validate_weight = validator('weight',
                                 allow_reuse=True,
                                 pre=True)(convert_to_decimal)

    _validate_record_type = validator('record_type', allow_reuse=True, pre=True)(allow_string_rep_of_enum)


class RecordEditReqSchema(BaseSchemaEditReqSchema):
    organization_id: Optional[int]
    user_id: Optional[int]
    import_from_id: Optional[int]
    export_to_id: Optional[int]
    record_type: Optional[RecordType]
    discount_id: Optional[int]
    fish_variant_id: Optional[int]
    weigh_place_id: Optional[int]
    weight: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS
    is_SP: Optional[bool]

    _validate_weight = validator('weight',
                                 allow_reuse=True,
                                 pre=True)(convert_to_decimal)

    _validate_record_type = validator('record_type', allow_reuse=True, pre=True)(allow_string_rep_of_enum)


class RecordListingReqSchema(BaseSchemaListingReqSchema):
    organization_id: Optional[int]
    user_id: Optional[int]
    import_from_id: Optional[int]
    export_to_id: Optional[int]
    record_type: Optional[RecordType]
    discount_id: Optional[int]
    fish_variant_id: Optional[int]
    weigh_place_id: Optional[int]
    is_SP: Optional[bool]

    _validate_record_type = validator('record_type', allow_reuse=True, pre=True)(allow_string_rep_of_enum)


class BillItemCreationReqSchema(BaseSchemaCreationReqSchema):
    bill_id: Optional[int]
    weight: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS
    price: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    fish_variant_id: int
    is_SP: bool = False

    _validate_decimal = validator('price', 'weight',
                                  allow_reuse=True,
                                  pre=True)(convert_to_decimal)


class BillItemEditReqSchema(BaseSchemaEditReqSchema):
    bill_id: Optional[int]
    weight: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS
    price: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    fish_variant_id: int
    is_SP: bool

    _validate_decimal = validator('price', 'weight',
                                  allow_reuse=True,
                                  pre=True)(convert_to_decimal)


class BillItemListingReqSchema(BaseSchemaListingReqSchema):
    bill_id: Optional[int]
    fish_variant_id: Optional[int]
    is_SP: Optional[bool]


class BillCreationReqSchema(BaseSchemaCreationReqSchema):
    bill_items: List[BillItemCreationReqSchema]
    organization_id: Optional[int]
    user_id: Optional[int]
    bill_place_id: Optional[int]
    price: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    discount_id: Optional[int]
    total_amount: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    billed_amount: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    discounted_price: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    pay_type: Optional[PayType]

    _validate_pay_type = validator('pay_type', allow_reuse=True, pre=True)(allow_string_rep_of_enum)

    _validate_decimal = validator('price', 'total_amount', 'billed_amount', 'discounted_price',
                                  allow_reuse=True,
                                  pre=True)(convert_to_decimal)


class BillEditReqSchema(BaseSchemaEditReqSchema):
    organization_id: Optional[int]
    user_id: Optional[int]
    bill_place_id: Optional[int]
    price: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    discount_id: Optional[int]
    total_amount: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    billed_amount: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    discounted_price: Optional[condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))]
    pay_type: Optional[PayType]
    is_active: bool

    _validate_pay_type = validator('pay_type', allow_reuse=True, pre=True)(allow_string_rep_of_enum)


class BillListingReqSchema(BaseSchemaListingReqSchema):
    organization_id: Optional[int]
    user_id: Optional[int]
    bill_place_id: Optional[int]
    discount_id: Optional[int]
    pay_type: Optional[PayType]

    _validate_pay_type = validator('pay_type', allow_reuse=True, pre=True)(allow_string_rep_of_enum)


class StockCreationReqSchema(BaseModel):
    place_id: Optional[int]
    fish_variant_id: int
    is_SP: bool = False
    weight: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS

    _validate_decimal = validator('weight',
                                  allow_reuse=True,
                                  pre=True)(convert_to_decimal)


class StockEditReqSchema(BaseModel):
    place_id: Optional[int]
    fish_variant_id: int
    is_SP: bool
    weight: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))
    weight_unit: WeightUnit = WeightUnit.KILOGRAMS

    _validate_decimal = validator('weight',
                                  allow_reuse=True,
                                  pre=True)(convert_to_decimal)


class StockListingReqSchema(BaseSchemaListingReqSchema):
    organization_id: Optional[int]
    place_id: Optional[int]
    fish_variant_id: Optional[int]
    is_SP: Optional[bool]


class ExpenseCreationReqSchema(BaseModel):
    organization_id: Optional[int]
    user_id: Optional[int]
    type_id: int
    desc: Optional[str]
    amount: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))

    _validate_amount = validator('amount',
                                 allow_reuse=True,
                                 pre=True)(convert_to_decimal)


class ExpenseEditReqSchema(BaseModel):
    organization_id: Optional[int]
    user_id: Optional[int]
    type_id: int
    desc: Optional[str]
    amount: condecimal(max_digits=10, decimal_places=2, ge=Decimal(0))

    _validate_amount = validator('amount',
                                 allow_reuse=True,
                                 pre=True)(convert_to_decimal)


class ExpenseListingReqSchema(BaseSchemaListingReqSchema):
    organization_id: Optional[int]
    user_id: Optional[int]
    type_id: Optional[int]
    desc: Optional[str]
