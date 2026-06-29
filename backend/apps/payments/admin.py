from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("ride", "amount_cents", "currency", "status", "created_at")
    search_fields = ("stripe_payment_intent_id",)

