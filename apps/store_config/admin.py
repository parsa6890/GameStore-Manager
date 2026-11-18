from django.contrib import admin
from .models import StoreSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not StoreSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("store_name", "browser_title", "brand_description")}),
        ("برندینگ", {"fields": ("logo", "mobile_logo", "banner", "primary_color", "secondary_color", "background_color")}),
        ("محتوا", {"fields": ("welcome_text", "address", "phone")}),
        ("QR Code", {"fields": ("qr_destination_url",)}),
    )