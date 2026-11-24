import secrets
import hashlib
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import Customer
from apps.consoles.models import ConsoleCapacity
from apps.games.models import GamePlatformVersion
from .models import Order, OrderItem, OrderStatus, OrderStatusHistory


class OrderError(Exception):
    """خطای منطقی ثبت سفارش"""
    pass


def generate_order_number():
    """شماره سفارش یکتا با فرمت GS-YYYYMMDD-XXXX"""
    for _ in range(10):
        date_part = timezone.now().strftime("%Y%m%d")
        random_part = secrets.token_hex(2).upper()
        number = f"GS-{date_part}-{random_part}"
        if not Order.objects.filter(order_number=number).exists():
            return number
    raise OrderError("خطا در تولید شماره سفارش یکتا. لطفاً دوباره تلاش کنید.")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@transaction.atomic
def create_order(customer: Customer, capacity_id: int, cart: dict) -> tuple:
    """
    ثبت سفارش با اعتبارسنجی کامل سمت سرور.
    خروجی: (order, raw_access_token)
    """
    # ۱. اعتبارسنجی سبد
    if not cart:
        raise OrderError("سبد خرید خالی است.")

    # ۲. دریافت ظرفیت از دیتابیس (نه از Session)
    try:
        capacity = ConsoleCapacity.objects.select_related(
            "console_model", "console_type"
        ).get(pk=capacity_id, is_active=True)
    except ConsoleCapacity.DoesNotExist:
        raise OrderError("ظرفیت انتخاب‌شده معتبر نیست.")

    # ۳. دریافت نسخه‌ها از دیتابیس
    version_ids = []
    for vid in cart.keys():
        try:
            version_ids.append(int(vid))
        except (ValueError, TypeError):
            raise OrderError("شناسه بازی نامعتبر است.")

    versions = GamePlatformVersion.objects.select_related(
        "game", "console_type"
    ).filter(id__in=version_ids, is_active=True)

    if len(versions) != len(version_ids):
        raise OrderError("برخی از بازی‌های انتخابی معتبر نیستند یا غیرفعال شده‌اند.")

    versions_map = {v.id: v for v in versions}

    # ۴. بررسی سازگاری پلتفرم و نوع کنسول
    from apps.games.views import PLATFORM_MAP
    compatible_platforms = PLATFORM_MAP.get(capacity.console_model.name, [])

    for v in versions:
        if v.platform not in compatible_platforms:
            raise OrderError(f"بازی «{v.game.title_fa}» با کنسول شما سازگار نیست.")
        if v.console_type_id != capacity.console_type_id:
            raise OrderError(f"نسخه «{v.game.title_fa}» برای نوع کنسول شما موجود نیست.")

    # ۵. محاسبه مجموع حجم از دیتابیس (نه از مرورگر)
    total_volume = sum((v.size_gb for v in versions), Decimal("0"))

    # ۶. بررسی ظرفیت
    if total_volume > capacity.usable_capacity:
        overflow = total_volume - capacity.usable_capacity
        raise OrderError(
            f"حجم بازی‌های انتخاب‌شده ({total_volume} GB) از ظرفیت قابل استفاده "
            f"({capacity.usable_capacity} GB) بیشتر است. "
            f"مقدار اضافه: {overflow} GB. لطفاً بازی‌های انتخابی خود را ویرایش کنید."
        )

    # ۷. تولید شماره سفارش و توکن
    order_number = generate_order_number()
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    # ۸. ایجاد سفارش
    order = Order.objects.create(
        order_number=order_number,
        customer=customer,
        console_model=capacity.console_model,
        console_capacity=capacity,
        console_type_snapshot=capacity.console_type.name,
        nominal_capacity_snapshot=capacity.nominal_capacity,
        usable_capacity_snapshot=capacity.usable_capacity,
        total_volume_snapshot=total_volume,
        status=OrderStatus.NEW,
        access_token_hash=token_hash,
    )

    # ۹. ایجاد آیتم‌ها با Snapshot
    order_items = []
    for v in versions:
        order_items.append(OrderItem(
            order=order,
            game_version=v,
            game_title_snapshot=v.game.title_fa,
            platform_snapshot=v.get_platform_display(),
            version_name_snapshot=v.version_name or "",
            size_gb_snapshot=v.size_gb,
        ))
    OrderItem.objects.bulk_create(order_items)

    # ۱۰. ثبت تاریخچه وضعیت اولیه
    OrderStatusHistory.objects.create(
        order=order,
        old_status=OrderStatus.NEW,
        new_status=OrderStatus.NEW,
        note="ثبت اولیه سفارش توسط مشتری",
    )

    return order, raw_token


def update_order_status(order: Order, new_status: str, user=None, note: str = ""):
    """تغییر وضعیت سفارش + ثبت تاریخچه"""
    if new_status not in dict(OrderStatus.choices):
        raise OrderError("وضعیت نامعتبر است.")

    old_status = order.status
    if old_status == new_status:
        return

    with transaction.atomic():
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            note=note,
        )