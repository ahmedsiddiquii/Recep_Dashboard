from .bot.modules.LeadGenerater import Lead_Generator
from .bot.modules.Job_Scraper import *
from .models import Leads,Task,Job,JobTask
import threading
from django.utils import timezone
from datetime import datetime, timedelta

from time import sleep


def glass_door_thread(filter_url,no_of_leads,instance):
    keyword = filter_url
    no_of_jobs = no_of_leads
    obj = GlassDoor()
    driver = obj.initilize_driver(filter_url)
    # obj.login(driver,keyword)
    all_data = obj.scrap(driver, keyword, no_of_jobs)
    driver.close()

    print(all_data)
    for data in all_data:
        print(data)
        data['task_id'] = instance.id
        lead = Job(**data)
        lead.save()


def linkedin_thread(filter_url, no_of_leads, instance):
        keyword = filter_url
        no_of_jobs = no_of_leads
        obj = Linkedin()
        driver = obj.initilize_driver(filter_url)
        # obj.login(driver,keyword)
        all_data = obj.scrap(driver, no_of_jobs)
        driver.close()

        print(all_data)
        for data in all_data:
            print(data)
            data['task_id'] = instance.id
            lead = Job(**data)
            lead.save()



def indeed_thread(filter_url, no_of_leads, instance):
    keyword = filter_url
    no_of_jobs = no_of_leads
    obj = Indeed()
    driver = obj.initialize(filter_url)
    # obj.login(driver,keyword)
    all_data = obj.scrape(driver, keyword, no_of_jobs)
    driver.close()

    print(all_data)
    for data in all_data:
        print(data)
        data['task_id'] = instance.id
        lead = Job(**data)
        lead.save()

def talent_thread(filter_url, no_of_leads, instance):
    keyword = filter_url
    no_of_jobs = no_of_leads
    obj = Talent()
    driver = obj.initialize(filter_url)
    # obj.login(driver,keyword)
    all_data = obj.scrape(driver, keyword, no_of_jobs)
    driver.close()

    print(all_data)
    for data in all_data:
        print(data)
        data['task_id']=instance.id
        lead = Job(**data)
        lead.save()

def do_thread(existing_data,linkedin_email,linkedin_password,no_of_leads,filter_url,id,status):
    if status=="lead":
        obj = Lead_Generator()
        obj.initialize(linkedin_email, linkedin_password, user_dir=False)
        all_data=obj.search_result(
            filter_url, lead_no=int(no_of_leads), existing_data=existing_data
        )
        print(all_data)
        for data in all_data:
            print(data)
            lead = Leads(**data)
            lead.save()
        task = Task.objects.get(id=id)
        task.status="completed"
        task.save()
def do_thread_job(existing_data,instance):

    linkedin_link=instance.linkedin_link
    glassdoor_link=instance.glassdoor_link
    indeed_link=instance.indeed_link
    threads=[]
    # print([linkedin_link,glassdoor_link,indeed_link])
    if linkedin_link!="":
        s1=threading.Thread(target=linkedin_thread,args=(linkedin_link,10,instance,))

        threads.append(s1)


    if glassdoor_link!="":
        s2=threading.Thread(target=glass_door_thread,args=(glassdoor_link,10,instance,))

        threads.append(s2)


    if indeed_link!="":
        s3=threading.Thread(target=indeed_thread,args=(indeed_link,10,instance,))

        threads.append(s3)
    for t in threads:
        t.start()
        sleep(0.5)
    for t in threads:
        t.join()

    instance.last_updated = timezone.now()
    instance.next_update = instance.last_updated + timedelta(days=1)
    instance.activity_status = "Stop"
    instance.save()

def thread_custom_email_job(object):
    website=object.company_website
    emails=scrape_contact_info(website)
    object.company_email = emails
    object.save()




