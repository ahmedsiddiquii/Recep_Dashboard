from .bot.modules.LeadGenerater import Lead_Generator
from .bot.modules.Job_Scraper import *
from .models import Leads,Task,Job
import threading


def glass_door_thread(filter_url,no_of_leads,id):
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
        lead = Job(**data)
        lead.save()
    task = Task.objects.get(id=id)
    task.status = "completed"
    task.save()

def linkedin_thread(filter_url, no_of_leads, id):
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
            lead = Job(**data)
            lead.save()
        task = Task.objects.get(id=id)
        task.status = "completed"
        task.save()


def indeed_thread(filter_url, no_of_leads, id):
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
        lead = Job(**data)
        lead.save()
    task = Task.objects.get(id=id)
    task.status = "completed"
    task.save()
def talent_thread(filter_url, no_of_leads, id):
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
        lead = Job(**data)
        lead.save()
    task = Task.objects.get(id=id)
    task.status = "completed"
    task.save()
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
    else:
        if "linkedin" in filter_url:
            l = threading.Thread(target=linkedin_thread, args=(filter_url, no_of_leads, id,))
            l.start()
        if "glassdoor" in filter_url:
            g = threading.Thread(target=glass_door_thread, args=(filter_url, no_of_leads, id,))
            g.start()
        if "talent" in filter_url:
            t = threading.Thread(target=talent_thread, args=(filter_url, no_of_leads, id,))
            t.start()
        if "indeed" in filter_url:
            i = threading.Thread(target=indeed_thread, args=(filter_url, no_of_leads, id,))
            i.start()




