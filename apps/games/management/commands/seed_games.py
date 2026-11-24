from apps.consoles.models import ConsoleType
from django.core.management.base import BaseCommand
from apps.games.models import (
    GameCategory, Genre, Game, GamePlatformVersion,
    AgeGroup, ViolenceLevel, Platform,
)


CATEGORIES = [
    "فوتبال", "ورزشی", "اکشن", "ماجراجویی", "جهان‌باز",
    "تیراندازی", "اول‌شخص", "سوم‌شخص", "مسابقه‌ای",
    "مبارزه‌ای", "نقش‌آفرینی", "ترسناک", "خانوادگی",
    "استراتژیک", "بازی‌های مناسب کودکان",
]

GENRES = [
    "Sports", "Action", "Adventure", "Open World", "Shooter",
    "FPS", "Third Person", "Racing", "Fighting", "RPG",
    "Horror", "Family", "Strategy", "Kids", "Puzzle", "Educational",
]

GAMES_DATA = [
    {
        "title_fa": "فیفا ۲۴", "title_en": "EA Sports FC 24",
        "categories": ["فوتبال", "ورزشی"],
        "genres": ["Sports"],
        "age_group": AgeGroup.AGE_3_6,
        "is_kid_friendly": True, "is_family_friendly": True,
        "violence_level": ViolenceLevel.NONE,
        "recommended_age": 3,
        "versions": {
            "copy": [(Platform.PS4, 45.5), (Platform.PS5, 52.0), (Platform.XBOX_ONE, 45.5), (Platform.XBOX_SERIES_X, 52.0)],
            "account": [(Platform.PS4, 50.0), (Platform.PS5, 55.0)],
            "normal": [(Platform.PS4, 45.5), (Platform.PS5, 52.0)],
        },
    },
    {
        "title_fa": "اسپایدرمن ۲", "title_en": "Marvel's Spider-Man 2",
        "categories": ["اکشن", "ماجراجویی", "جهان‌باز"],
        "genres": ["Action", "Adventure", "Open World"],
        "age_group": AgeGroup.AGE_13_PLUS,
        "is_kid_friendly": False, "is_family_friendly": False,
        "violence_level": ViolenceLevel.MEDIUM,
        "recommended_age": 13,
        "versions": {
            "copy": [(Platform.PS5, 98.0), (Platform.PS5_SLIM, 98.0)],
            "account": [(Platform.PS5, 105.0)],
            "normal": [(Platform.PS5, 98.0)],
        },
    },
    {
        "title_fa": "ماینکرفت", "title_en": "Minecraft",
        "categories": ["خانوادگی", "بازی‌های مناسب کودکان", "ماجراجویی"],
        "genres": ["Family", "Kids", "Adventure"],
        "age_group": AgeGroup.AGE_7_9,
        "is_kid_friendly": True, "is_family_friendly": True,
        "violence_level": ViolenceLevel.LOW,
        "recommended_age": 7,
        "versions": {
            "copy": [(Platform.PS4, 1.5), (Platform.PS5, 1.5), (Platform.XBOX_ONE, 1.5), (Platform.XBOX_SERIES_X, 1.5)],
            "account": [(Platform.PS4, 1.5), (Platform.PS5, 1.5)],
            "normal": [(Platform.PS4, 1.5), (Platform.PS5, 1.5)],
        },
    },
    {
        "title_fa": "کال آو دیوتی: وارزون", "title_en": "Call of Duty: Warzone",
        "categories": ["تیراندازی", "اول‌شخص", "اکشن"],
        "genres": ["Shooter", "FPS", "Action"],
        "age_group": AgeGroup.AGE_13_PLUS,
        "is_kid_friendly": False, "is_family_friendly": False,
        "violence_level": ViolenceLevel.HIGH,
        "recommended_age": 16,
        "versions": {
            "copy": [(Platform.PS4, 120.0), (Platform.PS5, 130.0), (Platform.XBOX_ONE, 120.0), (Platform.XBOX_SERIES_X, 130.0)],
            "account": [(Platform.PS4, 125.0), (Platform.PS5, 135.0)],
            "normal": [(Platform.PS4, 120.0), (Platform.PS5, 130.0)],
        },
    },
    {
        "title_fa": "گاد آو وار: راگناروک", "title_en": "God of War Ragnarök",
        "categories": ["اکشن", "ماجراجویی"],
        "genres": ["Action", "Adventure"],
        "age_group": AgeGroup.AGE_13_PLUS,
        "is_kid_friendly": False, "is_family_friendly": False,
        "violence_level": ViolenceLevel.HIGH,
        "recommended_age": 18,
        "versions": {
            "copy": [(Platform.PS4, 84.0), (Platform.PS5, 84.0)],
            "account": [(Platform.PS4, 90.0), (Platform.PS5, 90.0)],
            "normal": [(Platform.PS4, 84.0), (Platform.PS5, 84.0)],
        },
    },
    {
        "title_fa": "فورت‌نایت", "title_en": "Fortnite",
        "categories": ["اکشن", "تیراندازی", "خانوادگی"],
        "genres": ["Action", "Shooter", "Family"],
        "age_group": AgeGroup.AGE_10_12,
        "is_kid_friendly": True, "is_family_friendly": True,
        "violence_level": ViolenceLevel.LOW,
        "recommended_age": 10,
        "versions": {
            "copy": [(Platform.PS4, 30.0), (Platform.PS5, 35.0), (Platform.XBOX_ONE, 30.0), (Platform.XBOX_SERIES_X, 35.0)],
            "account": [(Platform.PS4, 35.0), (Platform.PS5, 40.0)],
            "normal": [(Platform.PS4, 30.0), (Platform.PS5, 35.0)],
        },
    },
    {
        "title_fa": "ماریو کارت ۸", "title_en": "Mario Kart 8 Deluxe",
        "categories": ["مسابقه‌ای", "خانوادگی", "بازی‌های مناسب کودکان"],
        "genres": ["Racing", "Family", "Kids"],
        "age_group": AgeGroup.AGE_3_6,
        "is_kid_friendly": True, "is_family_friendly": True,
        "violence_level": ViolenceLevel.NONE,
        "recommended_age": 3,
        "versions": {
            "copy": [(Platform.PS4, 7.0), (Platform.PS5, 7.0)],
            "account": [(Platform.PS4, 7.0), (Platform.PS5, 7.0)],
            "normal": [(Platform.PS4, 7.0), (Platform.PS5, 7.0)],
        },
    },
    {
        "title_fa": "الدن رینگ", "title_en": "Elden Ring",
        "categories": ["نقش‌آفرینی", "اکشن", "جهان‌باز"],
        "genres": ["RPG", "Action", "Open World"],
        "age_group": AgeGroup.AGE_13_PLUS,
        "is_kid_friendly": False, "is_family_friendly": False,
        "violence_level": ViolenceLevel.HIGH,
        "recommended_age": 18,
        "versions": {
            "copy": [(Platform.PS4, 60.0), (Platform.PS5, 60.0), (Platform.XBOX_ONE, 60.0), (Platform.XBOX_SERIES_X, 60.0)],
            "account": [(Platform.PS4, 65.0), (Platform.PS5, 65.0)],
            "normal": [(Platform.PS4, 60.0), (Platform.PS5, 60.0)],
        },
    },
]


class Command(BaseCommand):
    help = "Seed game categories, genres and sample games"

    def handle(self, *args, **options):
        # Categories
        for cat_name in CATEGORIES:
            slug = cat_name.replace(" ", "-").replace("‌", "-").lower()
            _, created = GameCategory.objects.get_or_create(
                name=cat_name, defaults={"slug": slug, "is_active": True}
            )
            if created:
                self.stdout.write(f"  ✓ Category: {cat_name}")

        # Genres
        for genre_name in GENRES:
            slug = genre_name.lower().replace(" ", "-")
            _, created = Genre.objects.get_or_create(
                name=genre_name, defaults={"slug": slug, "is_active": True}
            )
            if created:
                self.stdout.write(f"  ✓ Genre: {genre_name}")

        # Games
        for game_data in GAMES_DATA:
            versions = game_data.pop("versions")
            cats = game_data.pop("categories", [])
            gens = game_data.pop("genres", [])

            game, created = Game.objects.get_or_create(
                title_en=game_data["title_en"], defaults=game_data
            )
            if created:
                self.stdout.write(f"  ✓ Game: {game_data['title_en']}")

            # Categories & Genres
            for cat_name in cats:
                cat = GameCategory.objects.filter(name=cat_name).first()
                if cat:
                    game.categories.add(cat)
            for gen_name in gens:
                gen = Genre.objects.filter(name=gen_name).first()
                if gen:
                    game.genres.add(gen)

            # Versions (per console_type)
            for type_slug, version_list in versions.items():
                console_type = ConsoleType.objects.get(slug=type_slug)
                for platform, size in version_list:
                    _, v_created = GamePlatformVersion.objects.get_or_create(
                        game=game,
                        platform=platform,
                        console_type=console_type,
                        version_name="",
                        defaults={"size_gb": size, "is_active": True},
                    )
                    if v_created:
                        self.stdout.write(
                            f"    ✓ Version: {game.title_en} - {console_type.name} - {platform} - {size}GB"
                        )

        self.stdout.write(self.style.SUCCESS("\n✅ Game seed done!"))