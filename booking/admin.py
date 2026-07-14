from django.contrib import admin
from unfold.admin import ModelAdmin
from .models.coupon import Coupon
from .models.booking import Booking

@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_spend', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)

@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = ('booking_uid', 'guest_name', 'room', 'check_in', 'check_out', 'total', 'status')
    list_filter = ('status', 'check_in', 'room')
    search_fields = ('booking_uid', 'guest_name', 'guest_email', 'guest_phone')
    readonly_fields = ('booking_uid', 'created_at', 'updated_at')
