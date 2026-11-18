from django.contrib import admin
from .models import ConsoleBrand, ConsoleModel, ConsoleCapacity


class ConsoleCapacityInline(admin.TabularInline):
    model = ConsoleCapacity
    extra = 1
    fields = ("nominal_capacity", "usable_capacity", "is_active")


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
    list_display = ("console_model", "nominal_capacity", "usable_capacity", "is_active")
    list_filter = ("is_active", "console_model__brand")
    search_fields = ("console_model__name",)