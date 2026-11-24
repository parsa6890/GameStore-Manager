from django.contrib import admin
from .models import ConsoleBrand, ConsoleType, ConsoleModel, ConsoleCapacity


@admin.register(ConsoleType)
class ConsoleTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ConsoleCapacityInline(admin.TabularInline):
    model = ConsoleCapacity
    extra = 1
    fields = ("console_type", "nominal_capacity", "usable_capacity", "is_active")


@admin.register(ConsoleBrand)
class ConsoleBrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(ConsoleModel)
class ConsoleModelAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "is_active", "created_at")
    list_filter = ("brand", "is_active")
    search_fields = ("name", "brand__name")
    inlines = [ConsoleCapacityInline]


@admin.register(ConsoleCapacity)
class ConsoleCapacityAdmin(admin.ModelAdmin):
    list_display = ("console_model", "console_type", "nominal_capacity", "usable_capacity", "is_active")
    list_filter = ("is_active", "console_type", "console_model__brand")
    search_fields = ("console_model__name",)