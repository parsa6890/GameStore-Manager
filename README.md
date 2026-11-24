\# GameStore Manager



سامانه مدیریت سفارش بازی کنسول — فروشگاه خدمات بازی



\## ویژگی‌ها



\- 🎮 پنل مشتری: انتخاب کنسول (برند/مدل/نوع/ظرفیت)، لیست بازی‌های سازگار، فیلتر و جستجو

\- 📊 محاسبه لحظه‌ای حجم + نوار ظرفیت + پاپ‌آپ هشدار عبور از ظرفیت

\- 🛒 سبد خرید Sticky + امکان ویرایش/حذف

\- 📦 ثبت سفارش با اعتبارسنجی کامل سمت سرور + تراکنش اتمیک + Snapshot

\- ⚙️ پنل مدیریت: داشبورد، سفارش‌ها، مشتریان، تنظیمات، QR Code

\- 🖨️ چاپ سفارش با CSS Print

\- 🎨 تم تاریک گیمینگ (بنفش/آبی نئون) + RTL کامل

\- 🔐 امنیت: CSRF، XSS، Session امن، توکن دسترسی تصادفی



\## تکنولوژی



\- Python 3.14 + Django 5.2.7

\- PostgreSQL 17

\- Tailwind CSS (CDN)

\- HTMX (آماده برای توسعه)

\- Pillow + qrcode



\## نصب سریع (Development)



```bash

\# 1. Clone

git clone git@github.com:USERNAME/GameStore-Manager.git

cd GameStore-Manager



\# 2. Virtual Environment

python -m venv .venv

.venv\\Scripts\\activate  # Windows

\# source .venv/bin/activate  # Linux/Mac



\# 3. Install

pip install -r requirements.txt



\# 4. Environment

copy .env.example .env

\# سپس مقادیر .env را پر کنید



\# 5. Database

python manage.py migrate



\# 6. Seed Data

python manage.py seed\_consoles

python manage.py seed\_games



\# 7. Superuser

python manage.py createsuperuser



\# 8. Run

python manage.py runserver

