# Cron setup (every 3 hours)

```bash
0 */3 * * * cd /workspace/InclinicRedeveloped && /usr/bin/python manage.py sync_reporting >> /var/log/inclinic_sync.log 2>&1
```
