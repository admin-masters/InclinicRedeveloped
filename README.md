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

## Media files in development

- Uploaded files are served through `/media/` in `DEBUG=True`.
- Example: a file stored at `pdfs/RFAAWSCommands.pdf` is available at `/media/pdfs/RFAAWSCommands.pdf`, not `/pdfs/RFAAWSCommands.pdf`.

## Cron (every 3 hours)

Use the entry documented in `deploy/cron.md`.

## Reporting refresh during manual testing

- Brand Report now includes a **Sync Latest Transactions** button to trigger `sync_reporting` immediately.
- Production scheduling should still use cron every 3 hours.
