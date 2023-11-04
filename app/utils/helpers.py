import re
import uuid

from decimal import Decimal

from django.utils import translation

from app.fish.enums import WeightUnit
from app.logistics.enums import PayType, RecordType
from app.organizations.enums import PlaceType
from app.users.enums import Designation
from app.utils.constants import CacheKeys, SMS

import urllib.request
import urllib.parse
from django.conf import settings

import re
import uuid
from decimal import Decimal
from urllib import request, parse
from django.conf import settings
from app.utils.constants import CacheKeys, SMS
from app.utils.serializers import EnumValueSerializer


def get_data_for_field(field, locale):
    mapping = {
        'Designation': Designation,
        'WeightUnit': WeightUnit,
        'RecordType': RecordType,
        'PlaceType': PlaceType,
        'PayType': PayType,

    }
    translation.activate(locale)
    enum_class = mapping.get(field)
    data = EnumValueSerializer(enum_class.choices, many=True, context={'field': field, 'enum_class': enum_class}).data
    data = {
        "display_data": {
            "name": field,
            "name_vernacular": field,
        },
        "values": data
    }
    translation.deactivate()
    return data


def allow_string_rep_of_enum(x):
    """Convert string representation of enum to integer."""
    return int(x) if isinstance(x, str) else x


def convert_to_decimal(x):
    """Convert value to decimal."""
    return Decimal(x)


def trim_mobile_no(x):
    """Trim mobile number to last 10 digits if longer than 10 digits."""
    return x[-10:]


def send_sms(numbers, message):
    """Send SMS to given numbers with the specified message."""
    data = parse.urlencode({
        'apikey': settings.TEXT_LOCAL_API_KEY,
        'numbers': numbers,
        'message': message,
        'sender': settings.SMS_SENDER,
        'test': settings.DEBUG
    }).encode('utf-8')

    with request.urlopen(request.Request(SMS.TEXTLOCAL_HOST), data) as f:
        return f.read()


def qdict_to_dict(qdict):
    """Convert a QueryDict to a Python dict."""
    return {k: v[0] if len(v) == 1 else v for k, v in qdict.lists()}


def get_serialized_exception(e):
    """Serialize exception data into a dictionary."""
    return {
        'error_message': str(e),
        'error_code': e.args[0] if e.args else None,
    }, None


def mobile_number_validation_check(mobile_no):
    """Validate mobile number format."""
    return (
        "Enter mobile number" if mobile_no is None else
        "Invalid mobile number" if re.match(r"\d{10}$", mobile_no) is None else
        None
    )


def generate_random_username():
    """Generate a random username based on UUID."""
    return str(uuid.uuid4()).replace("-", "")


def get_serialized_enum(enum, locale=None, field_name=None):
    """Serialize enum data into a dictionary."""
    return {
        "id": enum.value,
        "name": enum.name,
        "name_vernacular": str(enum.label),
        "icon_url": "",
    }


def format_value(value):
    if value is None:
        return "None"
    elif isinstance(value, list):
        return "~".join(map(str, sorted(value)))
    elif isinstance(value, (int, bool)):
        return str(value)
    else:
        return value


def build_cache_key(template_type: CacheKeys, **kwargs) -> str:
    """
    Centralized method to generate cache keys based on a template type and the provided keyword arguments.
    """
    formatted_args = {key: format_value(value) for key, value in kwargs.items()}
    return template_type.value.format(**formatted_args)


def build_user_filter_cache_key(
        search_queries: list[str] or None,
        organization_id: int or None,
        designation: list[int] or None,
        place_id: list[int] or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "search_queries": "~".join(search_queries) if search_queries else "None",
        "organization_id": organization_id if organization_id else "None",
        "designation": "/".join(map(str, sorted(designation))) if designation else "None",
        "place_id": "_".join(map(str, sorted(place_id))) if place_id else "None",
        "is_active": str(is_active) if is_active else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.USER_LIST.format(**args)
    return cache_key


def build_fish_filter_cache_key(
        name: str or None,
        organization_id: int or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "name": name if name else "None",
        "organization_id": organization_id if organization_id else "None",
        "is_active": str(is_active) if is_active else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.FISH_LIST.format(**args)
    return cache_key


def build_fish_variant_filter_cache_key(
        fish_id: int or None,
        name: str or None,
        organization_id: int or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "fish_id": fish_id if fish_id else "None",
        "name": name if name else "None",
        "organization_id": organization_id if organization_id else "None",
        "is_active": str(is_active) if is_active else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.FISH_VARIANT_LIST.format(**args)
    return cache_key


def build_discount_filter_cache_key(
        organization_id: int or None,
        name: str or None,
        type: int or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "type": type if type else "None",
        "name": name if name else "None",
        "organization_id": organization_id if organization_id else "None",
        "is_active": str(is_active) if is_active else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.DISCOUNT_LIST.format(**args)
    return cache_key


def build_price_history_cache_key(
        fish_id: int or None,
        fish_variant_id: int or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "fish_id": fish_id if fish_id else "None",
        "fish_variant_id": fish_variant_id if fish_variant_id else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.PRICE_HISTORY_LIST.format(**args)
    return cache_key


def build_place_filter_cache_key(
        organization_id: int or None,
        name: str or None,
        type: int or None,
        is_active: bool or None,
        center_id: int or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "organization_id": organization_id if organization_id else "None",
        "name": name if name else "None",
        "type": type if type else "None",
        "is_active": str(is_active) if is_active else "None",
        "center_id": center_id if center_id else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.PLACE_LIST.format(**args)
    return cache_key


def build_organization_filter_cache_key(
        name: str or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "name": name if name else "None",
        "is_active": str(is_active) if is_active else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.ORGANIZATION_LIST.format(**args)
    return cache_key


def build_record_filter_cache_key(
        organization_id: int or None,
        user_id: int or None,
        import_from_id: int or None,
        export_to_id: int or None,
        record_type: int or None,
        discount_id: int or None,
        fish_variant_id: int or None,
        weigh_place_id: int or None,
        is_SP: bool or None,
        is_active: bool or None,
        start_time: str or None,
        end_time: str or None,
        ordering: str or None,
        page: int or None,
        locale: str,
):
    args = {
        "organization_id": str(organization_id) if organization_id is not None else "None",
        "user_id": str(user_id) if user_id is not None else "None",
        "import_from_id": str(import_from_id) if import_from_id is not None else "None",
        "export_to_id": str(export_to_id) if export_to_id is not None else "None",
        "record_type": str(record_type) if record_type is not None else "None",
        "discount_id": str(discount_id) if discount_id is not None else "None",
        "fish_variant_id": str(fish_variant_id) if fish_variant_id is not None else "None",
        "weigh_place_id": str(weigh_place_id) if weigh_place_id is not None else "None",
        "is_SP": str(is_SP) if is_SP is not None else "None",
        "is_active": str(is_active) if is_active is not None else "None",
        "start_time": start_time if start_time is not None else "None",
        "end_time": end_time if end_time is not None else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page is not None else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.RECORD_LIST.format(**args)
    return cache_key


def build_expense_filter_cache_key(
        organization_id: int or None,
        user_id: int or None,
        type_id: int or None,
        desc: str or None,
        start_time: str or None,
        end_time: str or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "organization_id": organization_id if organization_id else "None",
        "user_id": user_id if user_id else "None",
        "type_id": type_id if type_id else "None",
        "desc": desc if desc else "None",
        "start_time": start_time if start_time else "None",
        "end_time": end_time if end_time else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.EXPENSE_LIST.format(**args)
    return cache_key


def build_expense_type_filter_cache_key(
        name: str or None,
        organization_id: int or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "name": name if name else "None",
        "organization_id": organization_id if organization_id else "None",
        "is_active": str(is_active) if is_active else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.EXPENSE_TYPE_LIST.format(**args)
    return cache_key


def build_bill_filter_cache_key(
        organization_id: int or None,
        user_id: int or None,
        bill_place_id: int or None,
        discount_id: int or None,
        pay_type: int or None,
        is_active: bool or None,
        start_time: str or None,
        end_time: str or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "organization_id": organization_id if organization_id else "None",
        "user_id": user_id if user_id else "None",
        "bill_place_id": bill_place_id if bill_place_id else "None",
        "discount_id": discount_id if discount_id else "None",
        "pay_type": str(pay_type) if pay_type else "None",
        "is_active": str(is_active) if is_active is not None else "None",
        "start_time": start_time if start_time else "None",
        "end_time": end_time if end_time else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.BILL_LIST.format(**args)
    return cache_key


def build_bill_item_filter_cache_key(
        bill_id: int or None,
        fish_variant_id: int or None,
        is_SP: bool or None,
        is_active: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "bill_id": bill_id if bill_id else "None",
        "fish_variant_id": fish_variant_id if fish_variant_id else "None",
        "is_SP": str(is_SP) if is_SP is not None else "None",
        "is_active": str(is_active) if is_active is not None else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.BILL_ITEM_LIST.format(**args)
    return cache_key


def build_stock_filter_cache_key(
        organization_id: int or None,
        place_id: int or None,
        fish_variant_id: int or None,
        is_SP: bool or None,
        ordering: str or None,
        page: int or None,
        locale,
):
    args = {
        "organization_id": organization_id if organization_id else "None",
        "place_id": place_id if place_id else "None",
        "fish_variant_id": fish_variant_id if fish_variant_id else "None",
        "is_SP": str(is_SP) if is_SP is not None else "None",
        "ordering": ordering if ordering else "None",
        "page": str(page) if page else "None",
        "locale": locale,
    }

    cache_key = CacheKeys.STOCK_LIST.value.format(**args)
    return cache_key

