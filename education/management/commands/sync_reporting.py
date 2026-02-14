import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from education.models import Event, ReportingEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync transaction events to reporting database in safe batches.'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=500)

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        events = list(Event.objects.order_by('created_at')[:batch_size])
        self.stdout.write(f'start sync count={len(events)}')
        transferred = 0
        for event in events:
            try:
                with transaction.atomic(using='reporting'):
                    ReportingEvent.objects.using('reporting').get_or_create(
                        id=event.id,
                        defaults={
                            'event_type': event.event_type,
                            'campaign_id': event.campaign_id,
                            'collateral_id': event.collateral_id,
                            'field_rep_id': event.field_rep_id,
                            'doctor_id': event.doctor_id,
                            'share_instance_id': event.share_instance_id,
                            'video_percentage': event.video_percentage,
                            'created_at': event.created_at,
                        }
                    )
                event.delete()
                transferred += 1
            except Exception as exc:
                logger.exception('sync_failed event=%s err=%s', event.id, exc)
        self.stdout.write(self.style.SUCCESS(f'end sync transferred={transferred} failed={len(events)-transferred}'))
