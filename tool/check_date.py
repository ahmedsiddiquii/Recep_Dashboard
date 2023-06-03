from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = 'Checks for changes in the system date'

    def handle(self, *args, **options):
        current_date = timezone.now().date()
        print("dateeee")
        # Perform your desired action here
        # This code will be executed whenever the management command is run
