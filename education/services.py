import secrets
from datetime import timedelta
from urllib.parse import quote
from django.utils import timezone
from .models import Doctor, Event, ShareInstance


def create_share(campaign, field_rep, doctor, collateral):
    share = ShareInstance.objects.create(
        short_code=secrets.token_urlsafe(8)[:12],
        campaign=campaign,
        collateral=collateral,
        field_rep=field_rep,
        doctor=doctor,
    )
    Event.objects.create(
        event_type='share_initiated',
        campaign=campaign,
        collateral=collateral,
        field_rep=field_rep,
        doctor=doctor,
        share_instance=share,
    )
    msg = collateral.whatsapp_template.replace('$collateralLinks', f'https://example.com/s/{share.short_code}/')
    return share, f'https://api.whatsapp.com/send?phone={doctor.whatsapp_number}&text={quote(msg)}'


def doctor_status(field_rep, doctor):
    latest_share = ShareInstance.objects.filter(field_rep=field_rep, doctor=doctor).order_by('-created_at').first()
    if not latest_share:
        return 'Send Message'
    clicked = Event.objects.filter(share_instance=latest_share, event_type='link_clicked').exists()
    if clicked:
        return 'Read'
    if latest_share.created_at < timezone.now() - timedelta(days=6):
        return 'Send Reminder'
    return 'Sent'


def ensure_link_clicked(share):
    if not Event.objects.filter(share_instance=share, event_type='link_clicked').exists():
        Event.objects.create(
            event_type='link_clicked',
            campaign=share.campaign,
            collateral=share.collateral,
            field_rep=share.field_rep,
            doctor=share.doctor,
            share_instance=share,
        )
