from enum import Enum

class Timeouts:
    SECONDS_10 = 10
    MINUTES_2 = 2 * 60
    MINUTES_10 = 10 * 60
    MINUTES_30 = 30 * 60
    HOUR_1 = 1 * 60 * 60
    HOUR_6 = 6 * 60 * 60
    HOUR_24 = 24 * 60 * 60
    DAY_5 = 5 * 24 * 60 * 60
    ONE_MONTH = 30 * 24 * 60 * 60


class CacheKeys(Enum):
    # LIST
    USER_LIST = "user_list:{is_active}:{organization_id}:{place_id}:{designation}:{ordering}:{search_queries}:{page}:{locale}"
    FISH_LIST = "fish_list:{organization_id}:{ordering}:{is_active}:{name}:{page}:{locale}"
    FISH_VARIANT_LIST = "fish_variant_list:{fish_id}:{ordering}:{organization_id}:{is_active}:{name}:{page}:{locale}"
    DISCOUNT_LIST = "discount_list:{organization_id}:{ordering}:{is_active}:{type}:{name}:{page}:{locale}"
    PRICE_HISTORY_LIST = "price_history_list:{fish_id}:{fish_variant}:{user_id}:{ordering}:{page}:{locale}"
    ORGANIZATION_LIST = "organization_list:{is_active}:{name}:{ordering}:{page}:{locale}"
    PLACE_LIST = "place_list:{organization_id}:{ordering}:{is_active}:{type}:{center_id}:{name}:{page}:{locale}"
    RECORD_LIST = "record_list:{organization_id}:{ordering}:{is_active}:{is_SP}:{start_time}:{end_time}:{user_id}:" \
                  "{import_from_id}:{export_to_id}:{record_type}:{discount_id}:{fish_variant_id}" \
                  ":{weigh_place_id}:{page}:{locale}"
    EXPENSE_TYPE_LIST = "expense_type_list:{organization_id}:{ordering}:{is_active}:{page}:{name}:{locale}"
    EXPENSE_LIST = "expense_list:{organization_id}:{is_active}:{ordering}:{type_id}:{start_time}:{end_time}:{user_id}:{desc}:{page}:{locale}"
    BILL_LIST = "bill_list:{organization_id}:{ordering}:{is_active}:{user_id}:{bill_place_id}:" \
                "{start_time}:{end_time}:{discount_id}:{pay_type}:{page}:{locale}"
    BILL_ITEM_LIST = "bill_item_list:{bill_id}:{ordering}:{is_active}:{is_SP}:{fish_variant_id}:{page}:{locale}"
    STOCK_LIST = "stock_list:{organization_id}:{ordering}:{place_id}:{fish_variant_id}:{is_SP}:{page}:{locale}"

    # DETAILS
    USER_DETAILS_BY_PK = "user_details_by_pk:{pk}:{locale}"
    FISH_DETAILS_BY_PK = "fish_details_by_pk:{pk}:{locale}"
    FISH_VARIANT_DETAILS_BY_PK = "fish_variant_details_by_pk:{pk}:{locale}"
    DISCOUNT_DETAILS_BY_PK = "discount_details_by_pk:{pk}:{locale}"
    PLACE_DETAILS_BY_PK = "place_details_by_pk:{pk}:{locale}"
    RECORD_DETAILS_BY_PK = "record_details_by_pk:{pk}:{locale}"
    EXPENSE_TYPE_DETAILS_BY_PK = "expense_type_details_by_pk:{pk}:{locale}"
    EXPENSE_DETAILS_BY_PK = "expense_details_by_pk:{pk}:{locale}"
    BILL_DETAILS_BY_PK = "bill_details_by_pk:{pk}:{locale}"
    BILL_ITEM_DETAILS_BY_PK = "bill_item_details_by_pk:{pk}:{locale}"
    STOCK_DETAILS_BY_PK = "stock_details_by_pk:{pk}:{locale}"


class SMS:
    OTP_LOGIN = "otp-{otp}"
    TEXTLOCAL_HOST = "https://api.textlocal.in/send/?"
