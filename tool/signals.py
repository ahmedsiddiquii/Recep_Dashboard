from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import JobTask,Job
import threading
from .scraper import *
from django.db.models.signals import post_migrate
from django.dispatch import Signal

@receiver(pre_save, sender=JobTask)
def update_job_task(sender, instance, **kwargs):
    if instance.last_updated is None or instance.last_updated.date() != timezone.now().date():
        if instance.status=="active":
            existing_data = [link for (link,) in Job.objects.filter(id=instance.id).values_list('source_link')]
            # do_thread(existing_data, linkedin_email, linkedin_pass, instance.no_of_leads, instance.navigator_link)
            s = threading.Thread(target=do_thread_job, args=(existing_data,instance))
            s.start()
            instance.activity_status="running"

            # Call your function here to perform additional updates
            # function_name(instance)

date_changed = Signal()

@receiver(date_changed)
def handle_date_change(sender, **kwargs):
    # Your code logic here
    print("Date changed!")
    objs=JobTask.objects.all()
    ids=[]
    for i in objs:
        ids.append(i.id)
    for id in ids:
        instance=JobTask.objects.get(id=id)
        if instance.last_updated is None or instance.last_updated.date() != timezone.now().date():

            if instance.status == "active":
                existing_data = [link for (link,) in Job.objects.filter(id=instance.id).values_list('source_link')]
                # do_thread(existing_data, linkedin_email, linkedin_pass, instance.no_of_leads, instance.navigator_link)

                if instance.activity_status!="running":
                    print(instance.activity_status)
                    instance.activity_status = "running"
                    instance.save()
                    instance = JobTask.objects.get(id=id)
                    s = threading.Thread(target=do_thread_job, args=(existing_data, instance))
                    s.start()

    # Call the specific function you want to trigger
