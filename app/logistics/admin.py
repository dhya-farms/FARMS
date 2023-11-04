from django.contrib import admin

from app.logistics.models import Record, BillItem, Bill, Stock, Expense

admin.site.register(Record)
admin.site.register(BillItem)
admin.site.register(Bill)
admin.site.register(Stock)
admin.site.register(Expense)
