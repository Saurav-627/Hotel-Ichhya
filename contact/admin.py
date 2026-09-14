from django.contrib import admin
from .models.branch import Branch
from .models.inquiry import ContactInquiry
from .models.inquiry_category import InquiryCategory

@admin.register(InquiryCategory)
class InquiryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'is_main', 'is_published')
    list_filter = ('is_main', 'is_published')
    list_editable = ('is_main', 'is_published')
    search_fields = ('name', 'address')

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'category', 'is_read', 'created_at')
    list_filter = ('category', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
