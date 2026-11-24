from django import forms
from django.core.validators import RegexValidator
from .models import Customer


class CustomerForm(forms.Form):
    """فرم ساده (نه ModelForm) برای جلوگیری از تداخل unique validation"""
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-[#1A1A2E] border border-purple-900/40 rounded-lg px-4 py-3 text-gray-100 focus:outline-none focus:border-purple-500 transition",
            "placeholder": "نام",
            "autofocus": True,
        }),
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-[#1A1A2E] border border-purple-900/40 rounded-lg px-4 py-3 text-gray-100 focus:outline-none focus:border-purple-500 transition",
            "placeholder": "نام خانوادگی",
        }),
    )
    mobile = forms.CharField(
        max_length=11,
        validators=[RegexValidator(r"^09\d{9}$", "شماره موبایل باید با ۰۹ شروع شده و ۱۱ رقم باشد.")],
        widget=forms.TextInput(attrs={
            "class": "w-full bg-[#1A1A2E] border border-purple-900/40 rounded-lg px-4 py-3 text-gray-100 focus:outline-none focus:border-purple-500 transition text-left",
            "placeholder": "09xxxxxxxxx",
            "dir": "ltr",
            "inputmode": "numeric",
            "maxlength": "11",
        }),
    )

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]
        if not mobile.isdigit():
            raise forms.ValidationError("شماره موبایل فقط باید شامل ارقام باشد.")
        return mobile