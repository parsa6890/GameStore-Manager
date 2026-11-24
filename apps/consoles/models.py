from django.db import models
from django.core.validators import MinValueValidator


class ConsoleBrand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام برند")
    logo = models.ImageField(upload_to="consoles/brands/", blank=True, null=True, verbose_name="لوگو")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "برند کنسول"
        verbose_name_plural = "برندهای کنسول"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ConsoleType(models.Model):
    """نوع کنسول: کپی‌خور / اکانتی / معمولی"""

    name = models.CharField(max_length=50, unique=True, verbose_name="نام نوع")
    slug = models.SlugField(max_length=60, unique=True, verbose_name="اسلاگ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نوع کنسول"
        verbose_name_plural = "انواع کنسول"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ConsoleModel(models.Model):
    brand = models.ForeignKey(
        ConsoleBrand,
        on_delete=models.PROTECT,
        related_name="models",
        verbose_name="برند",
    )
    name = models.CharField(max_length=150, verbose_name="نام مدل")
    image = models.ImageField(upload_to="consoles/models/", blank=True, null=True, verbose_name="تصویر")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مدل کنسول"
        verbose_name_plural = "مدل‌های کنسول"
        ordering = ["brand__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name"],
                name="unique_console_model_per_brand",
            )
        ]

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


class ConsoleCapacity(models.Model):
    console_model = models.ForeignKey(
        ConsoleModel,
        on_delete=models.CASCADE,
        related_name="capacities",
        verbose_name="مدل کنسول",
    )
    console_type = models.ForeignKey(
        ConsoleType,
        on_delete=models.PROTECT,
        related_name="capacities",
        verbose_name="نوع کنسول",
    )
    nominal_capacity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="ظرفیت اسمی (GB)",
    )
    usable_capacity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="ظرفیت قابل استفاده (GB)",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ظرفیت کنسول"
        verbose_name_plural = "ظرفیت‌های کنسول"
        ordering = ["console_model", "console_type", "nominal_capacity"]
        constraints = [
            models.UniqueConstraint(
                fields=["console_model", "console_type", "nominal_capacity"],
                name="unique_capacity_per_model_type",
            ),
            models.CheckConstraint(
                condition=models.Q(usable_capacity__lte=models.F("nominal_capacity")),
                name="usable_capacity_lte_nominal",
            ),
        ]

    def __str__(self):
        return f"{self.console_model} - {self.console_type} - {self.nominal_capacity}GB"