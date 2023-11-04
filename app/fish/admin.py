from django.contrib import admin

from app.fish.models import Fish, FishVariant, Discount, PriceHistory

admin.site.register(Fish)
admin.site.register(FishVariant)
admin.site.register(Discount)
admin.site.register(PriceHistory)
