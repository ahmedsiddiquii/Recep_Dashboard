


import os
import sys
import django

# Set up Django environment
sys.path.append(os.getcwd())  # Replace with the path to your Django project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_automation_tool.settings')  # Replace with your project's settings module

# Initialize Django
django.setup()

# Import the necessary modules after Django is initialized
import datetime
import time
from django.dispatch import Signal
from django.utils import timezone
from tool.signals import date_changed

def check_date():
    current_date = timezone.now().date()

    while True:
        now = timezone.now().date()
        if current_date != now:
            current_date = now
            date_changed.send(sender=None)  # Trigger the signal
        time.sleep(10)  # Check for date change every minute

if __name__ == "__main__":
    check_date()
