# InclinicRedeveloped

Production-oriented Django implementation for in-clinic education distribution across five flows:

- Publisher campaign + in-clinic setup
- Brand manager field-rep operations and reporting
- Field rep login + WhatsApp sharing
- Doctor verification + engagement tracking
- Cron sync from transaction DB to reporting DB

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=reporting
python manage.py test
```

## Multi-database

- `default`: transaction DB (operational writes)
- `reporting`: analytics DB (read-only from report views)

## Cron (every 3 hours)

Use the entry documented in `deploy/cron.md`.
