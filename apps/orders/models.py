import secrets
import hashlib
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from apps.accounts.models import Customer
from apps.consoles.models import ConsoleCapacity
from apps.games.models import GamePlatformVersion


def generate_access_token():
    """توکن تصادفی ۳۲ بایتی برای دسترسی مشتری به سفارش"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class OrderStatus(models.TextChoices):
    NEW = "new", "جدید"
    PENDING_REVIEW = "pending_review", "در انتظار بررسی"
    IN_PROGRESS = "in_progress", "در حال انجام"
    COMPLETED = "completed", "تکمیل‌شده"
    CANCELLED = "cancelled", "لغوشده"


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="شماره سفارش")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders", verbose_name="مشتری")
    console_model = models.ForeignKey(
        "consoles.ConsoleModel", on_delete=models.PROTECT, related_name="orders", verbose_name="مدل کنسول"
    )
    console_capacity = models.ForeignKey(ConsoleCapacity, on_delete=models.PROTECT, related_name="orders", verbose_name="ظرفیت کنسول")

    # Snapshot اطلاعات ظرفیت (برای مصونیت از تغییرات بعدی)
    nominal_capacity_snapshot = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="ظرفیت اسمی (Snapshot)")
    usable_capacity_snapshot = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="ظرفیت قابل استفاده (Snapshot)")
    total_volume_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"), verbose_name="مجموع حجم (Snapshot)")

    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW, db_index=True, verbose_name="وضعیت"
    )
    access_token_hash = models.CharField(max_length=64, db_index=True, verbose_name="هش توکن دسترسی")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["customer", "-created_at"]),
        ]

    def __str__(self):
        return f"#{self.order_number} - {self.customer.full_name}"

    @staticmethod
    def generate_order_number() -> str:
        """شماره سفارش یکتا با فرمت GS-YYYYMMDD-XXXX"""
        from django.utils import timezone
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = secrets.token_hex(2).upper()
        return f"GS-{date_part}-{random_part}"

    def set_access_token(self):
        """توکن خام برمی‌گرداند، فقط هش ذخیره می‌شود"""
        raw = generate_access_token()
        self.access_token_hash = hash_token(raw)
        return raw


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش")
    game_version = models.ForeignKey(
        GamePlatformVersion, on_delete=models.PROTECT, related_name="order_items", verbose_name="نسخه بازی"
    )

    # Snapshot برای مصونیت از تغییرات بعدی
    game_title_snapshot = models.CharField(max_length=200, verbose_name="نام بازی (Snapshot)")
    platform_snapshot = models.CharField(max_length=20, verbose_name="پلتفرم (Snapshot)")
    version_name_snapshot = models.CharField(max_length=100, blank=True, verbose_name="نام نسخه (Snapshot)")
    size_gb_snapshot = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="حجم (Snapshot)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["order", "game_version"], name="unique_game_version_per_order"),
        ]

    def __str__(self):
        return f"{self.game_title_snapshot} ({self.size_gb_snapshot}GB)"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history", verbose_name="سفارش")
    old_status = models.CharField(max_length=20, choices=OrderStatus.choices, verbose_name="وضعیت قبلی")
    new_status = models.CharField(max_length=20, choices=OrderStatus.choices, verbose_name="وضعیت جدید")
    changed_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تغییردهنده"
    )
    note = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تاریخچه وضعیت سفارش"
        verbose_name_plural = "تاریخچه وضعیت سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.order.order_number}: {self.old_status} → {self.new_status}"