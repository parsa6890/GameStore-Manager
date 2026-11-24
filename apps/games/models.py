from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class GameCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="اسلاگ")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته والد",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "دسته‌بندی بازی"
        verbose_name_plural = "دسته‌بندی‌های بازی"
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام ژانر")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="اسلاگ")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "ژانر"
        verbose_name_plural = "ژانرها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AgeGroup(models.TextChoices):
    UNDER_3 = "under_3", "زیر ۳ سال"
    AGE_3_6 = "3_6", "۳ تا ۶ سال"
    AGE_7_9 = "7_9", "۷ تا ۹ سال"
    AGE_10_12 = "10_12", "۱۰ تا ۱۲ سال"
    AGE_13_PLUS = "13_plus", "۱۳ سال به بالا"
    UNKNOWN = "unknown", "نامشخص"


class ViolenceLevel(models.TextChoices):
    NONE = "none", "بدون خشونت"
    LOW = "low", "خشونت محدود"
    MEDIUM = "medium", "خشونت متوسط"
    HIGH = "high", "خشونت بالا"
    UNKNOWN = "unknown", "نامشخص"


class Game(models.Model):
    title_fa = models.CharField(max_length=200, verbose_name="نام فارسی")
    title_en = models.CharField(max_length=200, db_index=True, verbose_name="نام انگلیسی")
    cover = models.ImageField(upload_to="games/covers/", blank=True, null=True, verbose_name="کاور")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    categories = models.ManyToManyField(GameCategory, blank=True, related_name="games", verbose_name="دسته‌بندی‌ها")
    genres = models.ManyToManyField(Genre, blank=True, related_name="games", verbose_name="ژانرها")

    recommended_age = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="حداقل سن پیشنهادی",
        validators=[MinValueValidator(0), MaxValueValidator(99)],
    )
    age_group = models.CharField(
        max_length=20, choices=AgeGroup.choices, default=AgeGroup.UNKNOWN,
        verbose_name="گروه سنی",
    )
    is_kid_friendly = models.BooleanField(default=False, verbose_name="مناسب کودکان")
    is_family_friendly = models.BooleanField(default=False, verbose_name="مناسب خانواده")
    violence_level = models.CharField(
        max_length=20, choices=ViolenceLevel.choices, default=ViolenceLevel.UNKNOWN,
        verbose_name="سطح خشونت",
    )
    content_notes = models.TextField(blank=True, verbose_name="توضیحات محتوایی")

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "بازی"
        verbose_name_plural = "بازی‌ها"
        ordering = ["title_en"]
        indexes = [
            models.Index(fields=["title_en"]),
            models.Index(fields=["title_fa"]),
            models.Index(fields=["is_active", "is_kid_friendly"]),
        ]

    def __str__(self):
        return f"{self.title_fa} ({self.title_en})"


class Platform(models.TextChoices):
    PS4 = "ps4", "PlayStation 4"
    PS4_SLIM = "ps4_slim", "PlayStation 4 Slim"
    PS4_PRO = "ps4_pro", "PlayStation 4 Pro"
    PS5 = "ps5", "PlayStation 5"
    PS5_SLIM = "ps5_slim", "PlayStation 5 Slim"
    PS5_PRO = "ps5_pro", "PlayStation 5 Pro"
    XBOX_ONE = "xbox_one", "Xbox One"
    XBOX_ONE_S = "xbox_one_s", "Xbox One S"
    XBOX_ONE_X = "xbox_one_x", "Xbox One X"
    XBOX_SERIES_S = "xbox_series_s", "Xbox Series S"
    XBOX_SERIES_X = "xbox_series_x", "Xbox Series X"


class GamePlatformVersion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="versions", verbose_name="بازی")
    platform = models.CharField(max_length=20, choices=Platform.choices, verbose_name="پلتفرم")
    console_type = models.ForeignKey(
        "consoles.ConsoleType",
        on_delete=models.PROTECT,
        related_name="game_versions",
        verbose_name="نوع کنسول",
    )
    version_name = models.CharField(max_length=100, blank=True, verbose_name="نام نسخه")
    size_gb = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="حجم (GB)",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات نسخه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "نسخه پلتفرمی بازی"
        verbose_name_plural = "نسخه‌های پلتفرمی بازی"
        ordering = ["game", "platform", "console_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["game", "platform", "console_type", "version_name"],
                name="unique_game_platform_type_version",
            ),
        ]
        indexes = [
            models.Index(fields=["platform", "console_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.game.title_en} - {self.get_platform_display()} - {self.console_type} - {self.size_gb}GB"