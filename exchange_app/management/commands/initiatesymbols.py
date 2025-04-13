from django.core.management.base import BaseCommand

from exchange_app.tasks import get_bitunix_symbols_task
from exchange_app.models import Symbol


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not Symbol.objects.filter(
            exchange__name="Bitunix"
        ).exists():
            get_bitunix_symbols_task.delay()
