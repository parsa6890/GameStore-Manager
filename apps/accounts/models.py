import re
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validate_iran_mobile(value):
    """اعتبارسنجی شماره موبایل ایرانی (۰۹xxxxxxxxx)"""
    if not re.match(r"^09\d{9}$", value):
        raise ValidationError("شماره موبایل باید با ۰۹ شروع شده و ۱۱ رقم باشد.")


mobile_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="شماره موبایل باید با ۰۹ شروع شده و ۱۱ رقم باشد.",
)


class Customer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    mobile = models.CharField(
        max_length=11,
        unique=True,
        validators=[mobile_validator, validate_iran_mobile],
        verbose_name="شماره موبایل",
        db_index=True,
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_verified = models.BooleanField(
        default=False,
        verbose_name="احراز هویت شده",
        help_text="آیا شماره موبایل با OTP تأیید شده است؟"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mobile"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        # نرمال‌سازی ارقام فارسی/عربی به لاتین
        translations = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
        self.mobile = self.mobile.translate(translations).strip()
        super().save(*args, **kwargs)
class OTPVerification(models.Model):
    """
    مدل آماده برای احراز هویت OTP در آینده.
    فعلاً استفاده نمی‌شود، اما ساختار آماده است.
    """
    mobile = models.CharField(max_length=11, db_index=True, verbose_name="شماره موبایل")
    code = models.CharField(max_length=6, verbose_name="کد OTP")
    is_used = models.BooleanField(default=False, verbose_name="استفاده شده")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="تاریخ انقضا")

    class Meta:
        verbose_name = "احراز هویت OTP"
        verbose_name_plural = "احراز هویت‌های OTP"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mobile", "is_used"]),
        ]

    def __str__(self):
        return f"{self.mobile} - {self.code} ({'استفاده شده' if self.is_used else 'فعال'})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at