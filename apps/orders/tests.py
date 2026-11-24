from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from apps.accounts.models import Customer
from apps.consoles.models import ConsoleBrand, ConsoleType, ConsoleModel, ConsoleCapacity
from apps.games.models import Game, GamePlatformVersion, Platform
from apps.orders.models import Order, OrderItem
from apps.orders.services import create_order, OrderError


class OrderCapacityTests(TestCase):
    """تست منطق ظرفیت و ثبت سفارش"""

    def setUp(self):
        # برند و مدل
        self.brand = ConsoleBrand.objects.create(name="Sony")
        self.console_type = ConsoleType.objects.create(name="کپی‌خور", slug="copy")
        self.model = ConsoleModel.objects.create(brand=self.brand, name="PlayStation 4 Slim")

        # ظرفیت: 100GB قابل استفاده
        self.capacity = ConsoleCapacity.objects.create(
            console_model=self.model,
            console_type=self.console_type,
            nominal_capacity=Decimal("120.00"),
            usable_capacity=Decimal("100.00"),
        )

        # مشتری
        self.customer = Customer.objects.create(
            first_name="علی", last_name="رضایی", mobile="09121234567"
        )

        # بازی‌ها
        self.game1 = Game.objects.create(title_fa="بازی ۱", title_en="Game 1")
        self.game2 = Game.objects.create(title_fa="بازی ۲", title_en="Game 2")

        self.version1 = GamePlatformVersion.objects.create(
            game=self.game1, platform=Platform.PS4_SLIM,
            console_type=self.console_type, size_gb=Decimal("40.00"),
        )
        self.version2 = GamePlatformVersion.objects.create(
            game=self.game2, platform=Platform.PS4_SLIM,
            console_type=self.console_type, size_gb=Decimal("50.00"),
        )

    def test_capacity_within_limit(self):
        """ثبت سفارش در محدوده ظرفیت"""
        cart = {str(self.version1.id): {"size_gb": 40.0}}
        order, token = create_order(self.customer, self.capacity.id, cart)
        self.assertEqual(order.total_volume_snapshot, Decimal("40.00"))
        self.assertEqual(order.items.count(), 1)

    def test_capacity_exceeded(self):
        """رد سفارش بیش از ظرفیت"""
        cart = {
            str(self.version1.id): {"size_gb": 40.0},
            str(self.version2.id): {"size_gb": 50.0},
        }
        # مجموع ۹۰ هست، پس با ظرفیت ۱۰۰ باید قبول بشه
        order, _ = create_order(self.customer, self.capacity.id, cart)
        self.assertEqual(order.total_volume_snapshot, Decimal("90.00"))

        # حالا یه بازی سوم با حجم ۲۰ اضافه می‌کنیم → ۱۱۰ > ۱۰۰
        game3 = Game.objects.create(title_fa="بازی ۳", title_en="Game 3")
        version3 = GamePlatformVersion.objects.create(
            game=game3, platform=Platform.PS4_SLIM,
            console_type=self.console_type, size_gb=Decimal("20.00"),
        )
        cart[str(version3.id)] = {"size_gb": 20.0}

        with self.assertRaises(OrderError):
            create_order(self.customer, self.capacity.id, cart)

    def test_snapshot_immutable(self):
        """Snapshot بعد از تغییر بازی تغییر نمی‌کند"""
        cart = {str(self.version1.id): {"size_gb": 40.0}}
        order, _ = create_order(self.customer, self.capacity.id, cart)

        # تغییر حجم بازی
        self.version1.size_gb = Decimal("99.00")
        self.version1.save()

        # سفارش قدیمی نباید تغییر کند
        item = order.items.first()
        self.assertEqual(item.size_gb_snapshot, Decimal("40.00"))

    def test_empty_cart_rejected(self):
        """سبد خالی رد می‌شود"""
        with self.assertRaises(OrderError):
            create_order(self.customer, self.capacity.id, {})

    def test_invalid_version_rejected(self):
        """نسخه نامعتبر رد می‌شود"""
        cart = {"999999": {"size_gb": 10.0}}
        with self.assertRaises(OrderError):
            create_order(self.customer, self.capacity.id, cart)


class CustomerTests(TestCase):
    """تست ثبت مشتری"""

    def test_new_customer_created(self):
        c = Customer.objects.create(first_name="رضا", last_name="احمدی", mobile="09351234567")
        self.assertEqual(c.full_name, "رضا احمدی")

    def test_duplicate_mobile_allowed_at_form_level(self):
        """شماره تکراری در سطح فرم خطا نمی‌دهد (منطق در view)"""
        Customer.objects.create(first_name="الف", last_name="ب", mobile="09121111111")
        # این تست فقط تایید می‌کند که فیلد unique در DB هست
        with self.assertRaises(Exception):
            Customer.objects.create(first_name="ج", last_name="د", mobile="09121111111")