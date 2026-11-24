from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "game_version", "game_title_snapshot", "platform_snapshot",
        "version_name_snapshot", "size_gb_snapshot",
    )
    can_delete = False


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "note", "created_at")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number", "customer", "console_model", "console_type_snapshot",
        "status", "total_volume_snapshot", "created_at",
    )
    list_filter = ("status", "created_at", "console_model__brand")
    search_fields = ("order_number", "customer__first_name", "customer__last_name", "customer__mobile")
    readonly_fields = (
        "order_number", "console_type_snapshot", "nominal_capacity_snapshot",
        "usable_capacity_snapshot", "total_volume_snapshot", "access_token_hash",
        "created_at", "updated_at",
    )
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = "created_at"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "game_title_snapshot", "platform_snapshot", "size_gb_snapshot")
    search_fields = ("order__order_number", "game_title_snapshot")


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "old_status", "new_status", "changed_by", "created_at")
    list_filter = ("new_status",)