from django.contrib import admin
from .models import GameCategory, Genre, Game, GamePlatformVersion


class GamePlatformVersionInline(admin.TabularInline):
    model = GamePlatformVersion
    extra = 1
    fields = ("platform", "version_name", "size_gb", "is_active")


@admin.register(GameCategory)
class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "title_en", "is_kid_friendly", "is_family_friendly", "is_active")
    list_filter = ("is_active", "is_kid_friendly", "is_family_friendly", "age_group", "violence_level")
    search_fields = ("title_fa", "title_en")
    filter_horizontal = ("categories", "genres")
    inlines = [GamePlatformVersionInline]


@admin.register(GamePlatformVersion)
class GamePlatformVersionAdmin(admin.ModelAdmin):
    list_display = ("game", "platform", "version_name", "size_gb", "is_active")
    list_filter = ("platform", "is_active")
    search_fields = ("game__title_fa", "game__title_en")