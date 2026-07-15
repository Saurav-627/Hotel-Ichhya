from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models.payment import Payment
from .models.payment_processor import PaymentProcessor, PaymentProcessorCurrency

class PaymentProcessorCurrencyInline(TabularInline):
    model = PaymentProcessorCurrency
    extra = 1

@admin.register(PaymentProcessor)
class PaymentProcessorAdmin(ModelAdmin):
    list_display = ('name', 'code', 'apply_tax', 'is_published')
    list_filter = ('apply_tax', 'is_published')
    search_fields = ('name', 'code')
    inlines = [PaymentProcessorCurrencyInline]

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('id', 'booking', 'gateway', 'get_currency_iso', 'transaction_id', 'amount', 'status', 'created_at')
    list_filter = ('gateway', 'status', 'created_at', 'currency')
    search_fields = ('transaction_id', 'booking__booking_uid', 'booking__guest_name')
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Currency')
    def get_currency_iso(self, obj):
        return obj.currency.iso_code if obj.currency else "-"


