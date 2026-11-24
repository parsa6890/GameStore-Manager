

\---



```markdown

\# راهنمای استقرار (Deployment)



\## پیش‌نیازها



\- Ubuntu 22.04 LTS (یا 24.04)

\- Python 3.12+

\- PostgreSQL 15+

\- Nginx

\- Gunicorn

\- Git



\## گام ۱: آماده‌سازی سرور



```bash

sudo apt update \&\& sudo apt upgrade -y

sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git


\## گام ۲: ساخت دیتابیس
sudo -u postgres psql

CREATE DATABASE gamestore_db;
CREATE USER gamestore_user WITH PASSWORD 'StrongPass123!';
ALTER ROLE gamestore_user SET client_encoding TO 'utf8';
ALTER ROLE gamestore_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gamestore_user SET timezone TO 'Asia/Tehran';
GRANT ALL PRIVILEGES ON DATABASE gamestore_db TO gamestore_user;
\c gamestore_db
GRANT ALL ON SCHEMA public TO gamestore_user;
ALTER SCHEMA public OWNER TO gamestore_user;
\q

\## گام ۳: Clone و نصب

cd /var/www/
sudo git clone git@github.com:USERNAME/GameStore-Manager.git
cd GameStore-Manager

sudo python3 -m venv .venv
sudo .venv/bin/pip install --upgrade pip
sudo .venv/bin/pip install -r requirements.txt

\## گام ۴: تنظیمات محیطی

sudo cp .env.example .env
sudo nano .env

\## گام ۵: Migration و Seed

sudo .venv/bin/python manage.py migrate
sudo .venv/bin/python manage.py seed_consoles
sudo .venv/bin/python manage.py seed_games
sudo .venv/bin/python manage.py createsuperuser
sudo .venv/bin/python manage.py collectstatic --noinput

\## گام ۶: Gunicorn

sudo nano /etc/systemd/system/gamestore.service

[Unit]
Description=GameStore Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/GameStore-Manager
Environment="DJANGO_SETTINGS_MODULE=config.settings.prod"
ExecStart=/var/www/GameStore-Manager/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gamestore.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl enable --now gamestore

\## گام ۷: Nginx

sudo nano /etc/nginx/sites-available/gamestore

server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/GameStore-Manager;
    }
    location /media/ {
        root /var/www/GameStore-Manager;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gamestore.sock;
    }
}

sudo ln -s /etc/nginx/sites-available/gamestore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

\## گام ۸: HTTPS با Certbot

sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

\## گام ۹: دسترسی‌ها

sudo chown -R www-data:www-data /var/www/GameStore-Manager
sudo chmod -R 755 /var/www/GameStore-Manager
sudo chmod -R 775 /var/www/GameStore-Manager/media

\## به‌روزرسانی

cd /var/www/GameStore-Manager
sudo git pull origin main
sudo .venv/bin/pip install -r requirements.txt
sudo .venv/bin/python manage.py migrate
sudo .venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gamestore

