from django.contrib import admin
from unfold.admin import ModelAdmin
from .models.payment import Payment

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('id', 'booking', 'gateway', 'transaction_id', 'amount', 'status', 'created_at')
    list_filter = ('gateway', 'status', 'created_at')
    search_fields = ('transaction_id', 'booking__booking_uid', 'booking__guest_name')
    readonly_fields = ('created_at', 'updated_at')
