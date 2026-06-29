from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class FleetProUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("FleetPro", {"fields": ("role", "phone_number", "stripe_customer_id")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

