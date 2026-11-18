from django.db import models
from django.core.exceptions import ValidationError


class StoreSettings(models.Model):
    """تنظیمات فروشگاه — Singleton (فقط یک رکورد)"""

    store_name = models.CharField(max_length=200, default="فروشگاه بازی", verbose_name="نام فروشگاه")
    logo = models.ImageField(upload_to="store/", blank=True, null=True, verbose_name="لوگو")
    mobile_logo = models.ImageField(upload_to="store/", blank=True, null=True, verbose_name="لوگوی موبایل")
    primary_color = models.CharField(max_length=7, default="#7C3AED", verbose_name="رنگ اصلی")
    secondary_color = models.CharField(max_length=7, default="#06B6D4", verbose_name="رنگ مکمل")
    background_color = models.CharField(max_length=7, default="#0F0F1E", verbose_name="رنگ پس‌زمینه")
    banner = models.ImageField(upload_to="store/", blank=True, null=True, verbose_name="بنر")
    welcome_text = models.TextField(blank=True, default="به فروشگاه بازی خوش آمدید", verbose_name="متن خوشامدگویی")
    address = models.TextField(blank=True, verbose_name="آدرس")
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    browser_title = models.CharField(max_length=200, default="GameStore", verbose_name="عنوان مرورگر")
    brand_description = models.TextField(blank=True, verbose_name="توضیحات برند")
    qr_destination_url = models.URLField(blank=True, verbose_name="آدرس مقصد QR")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات فروشگاه"
        verbose_name_plural = "تنظیمات فروشگاه"

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        # Singleton: فقط یک رکورد
        if not self.pk and StoreSettings.objects.exists():
            raise ValidationError("تنظیمات فروشگاه قبلاً ساخته شده است.")
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj