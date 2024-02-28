from typing import Optional

from django.conf import settings
from django.db.models import F, Q, Case, When, Value, Count
from django.utils import timezone
from django.utils import translation
from django.db import IntegrityError, transaction
from app.logistics.models import Record, Expense, Bill, BillItem, Stock
from app.logistics.schemas import BillItemCreationReqSchema
from app.utils.controllers import Controller
from app.utils.helpers import get_serialized_exception


class RecordController(Controller):
    model = Record

    def create_record(self, organization_id, user_id, import_from_id, export_to_id, record_type, discount_id, fish_id,
                      fish_variant_id, weigh_place_id, weight, weight_unit, is_SP, is_active):
        try:
            record = self.model.objects.create(
                organization_id=organization_id,
                user_id=user_id,
                import_from_id=import_from_id,
                export_to_id=export_to_id,
                record_type=record_type,
                discount_id=discount_id,
                fish_id=fish_id,
                fish_variant_id=fish_variant_id,
                weigh_place_id=weigh_place_id,
                weight=weight,
                weight_unit=weight_unit,
                is_SP=is_SP,
                is_active=is_active
            )
            return None, record
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_record(self, record_obj, organization_id, user_id, import_from_id, export_to_id, record_type, discount_id,
                    fish_id, fish_variant_id, weigh_place_id, weight, weight_unit, is_SP, is_active):
        try:
            record_obj.organization_id = organization_id
            record_obj.user_id = user_id
            record_obj.import_from_id = import_from_id
            record_obj.export_to_id = export_to_id
            record_obj.record_type = record_type
            record_obj.discount_id = discount_id
            record_obj.fish_id = fish_id
            record_obj.fish_variant_id = fish_variant_id
            record_obj.weigh_place_id = weigh_place_id
            record_obj.weight = weight
            record_obj.weight_unit = weight_unit
            record_obj.is_SP = is_SP
            record_obj.is_active = is_active

            record_obj.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, record_obj

    def filter_records(self,
                       organization_id,
                       user_id,
                       import_from_id,
                       export_to_id,
                       record_type,
                       discount_id,
                       fish_id,
                       fish_variant_id,
                       weigh_place_id,
                       is_SP,
                       is_active,
                       start_time,
                       end_time,
                       ordering):
        record_qs = self.get_valid_records()
        try:
            if organization_id:
                record_qs = record_qs.filter(organization_id=organization_id)
            if user_id:
                record_qs = record_qs.filter(user_id=user_id)
            if import_from_id:
                record_qs = record_qs.filter(import_from_id=import_from_id)
            if export_to_id:
                record_qs = record_qs.filter(export_to_id=export_to_id)
            if record_type:
                record_qs = record_qs.filter(record_type=record_type)
            if discount_id:
                record_qs = record_qs.filter(discount_id=discount_id)
            if fish_id:
                record_qs = record_qs.filter(fish_id=fish_id)
            if fish_variant_id:
                record_qs = record_qs.filter(fish_variant_id=fish_variant_id)
            if weigh_place_id:
                record_qs = record_qs.filter(weigh_place_id=weigh_place_id)
            if is_SP is not None:
                record_qs = record_qs.filter(is_SP=is_SP)
            if is_active is not None:
                record_qs = record_qs.filter(is_active=is_active)
            if start_time and end_time:
                record_qs = record_qs.filter(created_at__range=(start_time, end_time))
            ordering = ordering if ordering is not None else '-created_at'
            if ordering:
                record_qs = record_qs.order_by(ordering)

            return None, record_qs
        except Exception as e:
            return get_serialized_exception(e)

    def make_inactive(self, obj):
        try:
            record = self.model.objects.get(pk=obj.pk)
            record.is_active = False
            record.save()
        except self.model.DoesNotExist as e:
            return get_serialized_exception(e)
        return None, True

    def get_valid_records(self):
        return self.model.objects.all()


class BillController(Controller):
    def __init__(self):
        self.model = Bill

    def create_bill(self,
                    organization_id,
                    user_id,
                    bill_place_id,
                    price,
                    discount_id,
                    total_amount,
                    billed_amount,
                    discounted_price,
                    pay_type,
                    is_active):
        try:
            bill = self.model.objects.create(
                organization_id=organization_id,
                user_id=user_id,
                bill_place_id=bill_place_id,
                price=price,
                discount_id=discount_id,
                total_amount=total_amount,
                billed_amount=billed_amount,
                discounted_price=discounted_price,
                pay_type=pay_type,
                is_active=is_active
            )
            return None, bill
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_bill(self,
                  bill,
                  organization_id,
                  user_id,
                  bill_place_id,
                  price, discount_id,
                  total_amount, billed_amount, discounted_price, pay_type, is_active):
        try:
            bill.organization_id = organization_id
            bill.user_id = user_id
            bill.bill_place_id = bill_place_id
            bill.price = price
            bill.discount_id = discount_id
            bill.total_amount = total_amount
            bill.billed_amount = billed_amount
            bill.discounted_price = discounted_price
            bill.pay_type = pay_type
            bill.is_active = is_active

            bill.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, bill

    def filter_bills(self,
                     organization_id,
                     user_id,
                     bill_place_id,
                     discount_id,
                     pay_type,
                     is_active,
                     start_time,
                     end_time,
                     ordering
                     ):
        bill_qs = self.get_valid_bills()
        try:
            if organization_id:
                bill_qs = bill_qs.filter(organization_id=organization_id)

            if user_id:
                bill_qs = bill_qs.filter(user_id=user_id)

            if bill_place_id:
                bill_qs = bill_qs.filter(bill_place_id=bill_place_id)

            if discount_id:
                bill_qs = bill_qs.filter(discount_id=discount_id)

            if pay_type:
                bill_qs = bill_qs.filter(pay_type=pay_type)

            if is_active:
                bill_qs = bill_qs.filter(is_active=is_active)

            if start_time and end_time:
                bill_qs = bill_qs.filter(created_at__range=(start_time, end_time))
            ordering = ordering if ordering is not None else '-created_at'
            if ordering:
                bill_qs = bill_qs.order_by(ordering)
            return None, bill_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_bill_items_with_bill(self, bill):
        try:
            bill_items = bill.bill_items.all()
            return None, bill_items
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_bills(self):
        return self.model.objects.all()

    def make_inactive(self, obj):
        try:
            errors, data = super().make_inactive(obj)
            if errors:
                return errors, data
            obj.bill_items.update(is_active=False)
            obj.save()
        except Exception as e:
            return get_serialized_exception(e)
        return None, True


class BillItemController(Controller):
    def __init__(self):
        self.model = BillItem

    def create_bill_item(self,
                         bill_id,
                         weight,
                         weight_unit,
                         price,
                         fish_id,
                         fish_variant_id,
                         is_SP,
                         is_active):
        try:
            bill_item = self.model.objects.create(
                bill_id=bill_id,
                weight=weight,
                weight_unit=weight_unit,
                price=price,
                fish_id=fish_id,
                fish_variant_id=fish_variant_id,
                is_SP=is_SP,
                is_active=is_active
            )
            return None, bill_item
        except IntegrityError as e:
            return get_serialized_exception(e)

    def create_bulk_bill_items(self, bill_id, bill_items: [BillItemCreationReqSchema]):
        try:

            bill_items = [
                self.model(
                    bill_id=bill_id,
                    weight=item.weight,
                    weight_unit=item.weight_unit,
                    price=item.price,
                    fish_id=item.fish_id,
                    fish_variant_id=item.fish_variant_id,
                    is_SP=item.is_SP,
                    is_active=item.is_active
                )
                for item in bill_items
            ]

            # Use a transaction to ensure the integrity of the database operation
            with transaction.atomic():
                bill_item_qs = BillItem.objects.bulk_create(bill_items)
            return None, bill_item_qs
        except Exception as e:
            return get_serialized_exception(e)

    def edit_bill_item(self,
                       bill_item,
                       bill_id,
                       weight,
                       weight_unit,
                       price,
                       fish_id,
                       fish_variant_id,
                       is_SP,
                       is_active):
        try:
            bill_item.bill_id = bill_id
            bill_item.weight = weight
            bill_item.weight_unit = weight_unit
            bill_item.price = price
            bill_item.fish_id = fish_id
            bill_item.fish_variant_id = fish_variant_id
            bill_item.is_SP = is_SP
            bill_item.is_active = is_active

            bill_item.save()
            return None, bill_item
        except IntegrityError as e:
            return get_serialized_exception(e)

    def filter_bill_items(self,
                          bill_id,
                          fish_id,
                          fish_variant_id,
                          is_SP,
                          is_active,
                          ordering):
        bill_item_qs = self.get_valid_bill_items()
        try:
            if bill_id:
                bill_item_qs = bill_item_qs.filter(bill_id=bill_id)
            if fish_id:
                bill_item_qs = bill_item_qs.filter(fish_id=fish_id)
            if fish_variant_id:
                bill_item_qs = bill_item_qs.filter(fish_variant_id=fish_variant_id)
            if is_SP is not None:
                bill_item_qs = bill_item_qs.filter(is_SP=is_SP)
            if is_active:
                bill_item_qs = bill_item_qs.filter(is_active=is_active)

            ordering = ordering if ordering is not None else 'fish_variant__name'
            if ordering:
                bill_item_qs = bill_item_qs.order_by(ordering)

            return None, bill_item_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_bill_items(self):
        return self.model.objects.select_related('fish_variant').all()


class StockController(Controller):
    def __init__(self):
        self.model = Stock

    def create_stock(self,
                     place_id,
                     fish_id,
                     fish_variant_id,
                     is_SP,
                     weight,
                     weight_unit):
        try:
            stock = self.model.objects.create(
                place_id=place_id,
                fish_id=fish_id,
                fish_variant_id=fish_variant_id,
                is_SP=is_SP,
                weight=weight,
                weight_unit=weight_unit
            )
            return None, stock
        except IntegrityError as e:
            return get_serialized_exception(e)

    def update_stock_weight(self,
                            place_id,
                            fish_id,
                            fish_variant_id,
                            is_SP,
                            weight,
                            weight_unit):
        try:
            stock, created = self.model.objects.get_or_create(
                place_id=place_id,
                fish_id=fish_id,
                fish_variant_id=fish_variant_id,
                is_SP=is_SP,
                weight_unit=weight_unit,
                defaults={'weight': weight, 'weight_unit': weight_unit}
            )

            if not created:
                # Update the weight if the object was retrieved, not created
                self.model.objects.filter(
                    place_id=place_id,
                    fish_id=fish_id,
                    fish_variant_id=fish_variant_id,
                    is_SP=is_SP,
                    weight_unit=weight_unit
                ).update(weight=F('weight') + weight)
            return None, stock
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_stock(self,
                   stock,
                   place_id,
                   fish_id,
                   fish_variant_id,
                   is_SP,
                   weight,
                   weight_unit):
        try:
            stock.place_id = place_id
            stock.fish_id = fish_id
            stock.fish_variant_id = fish_variant_id
            stock.is_SP = is_SP
            stock.weight = weight
            stock.weight_unit = weight_unit

            stock.save()
            return None, stock
        except IntegrityError as e:
            return get_serialized_exception(e)

    def filter_stocks(self,
                      organization_id,
                      place_id,
                      fish_id,
                      fish_variant_id,
                      is_SP,
                      ordering):
        stock_qs = self.get_valid_stocks()

        try:
            if organization_id:
                stock_qs = stock_qs.filter(place__organization_id=organization_id)

            if place_id:
                stock_qs = stock_qs.filter(place_id=place_id)

            if fish_id:
                stock_qs = stock_qs.filter(fish_id=fish_id)

            if fish_variant_id:
                stock_qs = stock_qs.filter(fish_variant_id=fish_variant_id)

            if is_SP is not None:
                stock_qs = stock_qs.filter(is_SP=is_SP)

            ordering = ordering if ordering is not None else '-weight'
            if ordering:
                stock_qs = stock_qs.order_by(ordering)

            return None, stock_qs
        except Exception as e:
            return get_serialized_exception(e)

    def get_valid_stocks(self):
        return self.model.objects.select_related('place', 'fish_variant').all()


class ExpenseController(Controller):
    def __init__(self):
        self.model = Expense

    def create_expense(self, organization_id, user_id, expense_date, type_id, desc, amount):
        try:
            expense = self.model.objects.create(
                organization_id=organization_id,
                user_id=user_id,
                expense_date=expense_date,
                type_id=type_id,
                desc=desc,
                amount=amount
            )
            return None, expense
        except IntegrityError as e:
            return get_serialized_exception(e)

    def edit_expense(self, expense, organization_id, user_id, expense_date, type_id, desc, amount):
        try:
            expense.organization_id = organization_id
            expense.user_id = user_id
            expense.expense_date = expense_date
            expense.type_id = type_id
            expense.desc = desc
            expense.amount = amount
            expense.save()
        except IntegrityError as e:
            return get_serialized_exception(e)
        return None, expense

    def filter_expenses(self,
                        organization_id,
                        user_id,
                        type_id,
                        desc,
                        start_time,
                        end_time,
                        ordering
                        ):
        expense_qs = self.get_valid_expenses()

        try:
            if organization_id:
                expense_qs = expense_qs.filter(organization_id=organization_id)
            if user_id:
                expense_qs = expense_qs.filter(user_id=user_id)
            if type_id:
                expense_qs = expense_qs.filter(type_id=type_id)
            if desc:
                expense_qs = expense_qs.filter(desc__icontains=desc)
            if start_time and end_time:
                expense_qs = expense_qs.filter(expense_date__range=(start_time, end_time))

            if ordering:
                expense_qs = expense_qs.order_by(ordering)
            else:
                expense_qs = expense_qs.order_by('-expense_date', 'amount')

            return None, expense_qs
        except Exception as e:
            return get_serialized_exception(e), None

    def get_valid_expenses(self):
        return self.model.objects.all()
