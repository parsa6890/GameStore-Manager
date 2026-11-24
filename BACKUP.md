

\---



\*\*فایل `BACKUP.md`:\*\*



```markdown

\# راهنمای پشتیبان‌گیری



\## پشتیبان‌گیری از دیتابیس



```bash

\# خروجی کامل

pg\_dump -U gamestore\_user -d gamestore\_db -F c -f /backup/gamestore\_$(date +%Y%m%d).dump



\# بازگردانی

pg\_restore -U gamestore\_user -d gamestore\_db -c /backup/gamestore\_YYYYMMDD.dump



\# پشتیبان‌گیری از رسانه‌ها



tar -czf /backup/media\_$(date +%Y%m%d).tar.gz /var/www/GameStore-Manager/media/



\# اسکریپت خودکار روزانه



sudo nano /etc/cron.daily/gamestore-backup



\#!/bin/bash

BACKUP\_DIR="/backup/gamestore"

DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP\_DIR"

pg\_dump -U gamestore\_user -d gamestore\_db -F c -f "$BACKUP\_DIR/db\_$DATE.dump"

tar -czf "$BACKUP\_DIR/media\_$DATE.tar.gz" /var/www/GameStore-Manager/media/

\# حذف بکاپ‌های قدیمی‌تر از 30 روز

find "$BACKUP\_DIR" -type f -mtime +30 -delete



sudo chmod +x /etc/cron.daily/gamestore-backup



\# بازیابی



\# دیتابیس

pg\_restore -U gamestore\_user -d gamestore\_db -c /backup/gamestore/db\_YYYYMMDD.dump



\# رسانه‌ها

tar -xzf /backup/gamestore/media\_YYYYMMDD.tar.gz -C /

