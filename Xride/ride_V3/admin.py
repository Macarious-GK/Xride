from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(XrideUser)
class XrideUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('wallet_balance', 'phone_number', 'address')}),
    )

admin.site.register(Car)
admin.site.register(Reservation)
admin.site.register(Payment)