from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from django.core import serializers
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import logout


from django.db.models.signals import post_save
from django.dispatch import receiver
from .scraper import *
import threading
from .bot.modules.LeadGenerater import Lead_Generator
from time import sleep
import json
from django.db.models import Q
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404



# Create
def logoutt(request):
    logout(request)
    return redirect(dashboard)
def login(request):

   if request.method == 'POST':
      print(request.POST)
      username = request.POST['username']
      password = request.POST['password']
      user = auth.authenticate(username=username, password=password)
      if user is not None:
         if user.is_active:
            auth.login(request, user)

         return redirect(dashboard)
      else:
         error="username or password is incorrect"
         return render(request,'index.html',{'error':error})
   else:
      return render(request, 'index.html')
def get_job_email(request):
    item_id=request.GET['id']
    job= get_object_or_404(Job, id=item_id)

    s=threading.Thread(target=thread_custom_email_job,args=(job,))
    s.start()
    return redirect(request.META.get('HTTP_REFERER'))
def jobs_task(request):
    if request.method=="POST":
        linkedin_link=request.POST['linkedin_filter_link']
        indeed_link = request.POST['indeed_filter_link']
        glassdoor_link = request.POST['glassdoor_filter_link']
        friendly_name = request.POST['friendly_name']
        obj=JobTask()
        obj.linkedin_link=linkedin_link
        obj.glassdoor_link=glassdoor_link
        obj.indeed_link=indeed_link
        obj.friendly_name=friendly_name
        obj.status="active"
        obj.save()
    jobtasks=JobTask.objects.all()
    return render(request,"job_task.html",{"page_obj":jobtasks})
def apply_export(request):

    #For job page
    if 'platform-option' in request.GET:
        print(request.GET)
        job_ids=""
        for i in request.GET:
            try:
                int(i)
                job_ids+=str(i)+","
            except:
                pass
        print(job_ids)
        if 'apply' in request.GET:

            filter_file=open("filters.json","r").read()
            try:
                filters=json.loads(filter_file)
            except:
                filters={}
            filters['job']={}

            filters['job']['email']=request.GET['email-option']

            filters['job']['number']=request.GET['number-option']

            filters['job']['platform'] = request.GET['platform-option']

            filter_file = open("filters.json","w")
            filter_file.write(json.dumps(filters))
            filter_file.close()
            return redirect(
                f"/search?search=&email-option={request.GET['email-option']}&number-option={request.GET['number-option']}&platform-option={request.GET['platform-option']}&jobs={job_ids}")

        if 'export' in request.GET:
            #export code here
            if request.GET['search']:
                query = request.GET['search']
            else:
                query = ""
            return redirect(
                f"/export?search={query}&email-option={request.GET['email-option']}&number-option={request.GET['number-option']}&platform-option={request.GET['platform-option']}&jobs={job_ids}")

        if 'search' in request.GET:
            query = request.GET['search']
            return redirect(
                f"/search?search={query}&email-option={request.GET['email-option']}&number-option={request.GET['number-option']}&platform-option={request.GET['platform-option']}&jobs={job_ids}")


    if 'size-option' in request.GET:

                if 'apply' in request.GET:
                    filter_file = open("filters.json", "r").read()
                    try:
                        filters = json.loads(filter_file)
                    except:
                        filters = {}
                    filters['lead'] = {}

                    filters['lead']['email'] = request.GET['email-option']

                    filters['lead']['number'] = request.GET['number-option']

                    filters['lead']['size'] = request.GET['size-option']

                    filter_file = open("filters.json", "w")
                    filter_file.write(json.dumps(filters))
                    filter_file.close()

                    return redirect(f"/search?search=&email-option={request.GET['email-option']}&number-option={request.GET['number-option']}&size-option={request.GET['size-option']}")

                if 'export' in request.GET:
                    # export code here
                    if request.GET['search']:
                        query=request.GET['search']
                    else:
                        query=""
                    return redirect(f"/export?search={query}&email-option={request.GET['email-option']}&number-option={request.GET['number-option']}&size-option={request.GET['size-option']}")

                if 'search' in request.GET:
                    query=request.GET['search']
                    return redirect(f"/search?search={query}&email-option={request.GET['email-option']}&number-option={request.GET['number-option']}&size-option={request.GET['size-option']}")


def export(request):
    if "size-option" in request.GET:
        if request.GET['search']:
            query = request.GET['search']

            leads = Leads.objects.filter(title__icontains=query)
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(email=None))
                    leads = leads.filter(~Q(email="NA"))
                else:
                    leads = leads.filter(Q(email=None) or Q(email="NA"))
                    # leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(phone_number=None))
                    leads = leads.filter(~Q(phone_number="NA"))
                else:
                    leads = leads.filter(Q(phone_number=None) or Q(phone_number="NA"))
                    # leads = leads.filter(phone_number="NA")
            if request.GET['size-option']:
                leads = leads.filter(employees__icontains=request.GET['size-option'])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="leads.csv"'

            writer = csv.writer(response)

            # Get all fields of the Lead model
            fields = [field.name for field in Leads._meta.get_fields()]

            writer.writerow(fields)  # Write header row



            for lead in leads:
                row = [getattr(lead, field) for field in fields]
                writer.writerow(row)  # Write each row with the object's attribute values

            return response

        else:
            query = ""
            leads = Leads.objects.all()
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(email=None))
                    leads = leads.filter(~Q(email="NA"))
                else:
                    leads = leads.filter(Q(email=None) or Q(email="NA"))
                    # leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(phone_number=None))
                    leads = leads.filter(~Q(phone_number="NA"))
                else:
                    leads = leads.filter(Q(phone_number=None) or Q(phone_number="NA"))
                    # leads = leads.filter(phone_number="NA")
            if request.GET['size-option']:
                leads = leads.filter(employees__icontains=request.GET['size-option'])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="leads.csv"'

            writer = csv.writer(response)

            # Get all fields of the Lead model
            fields = [field.name for field in Leads._meta.get_fields()]

            writer.writerow(fields)  # Write header row

            for lead in leads:
                row = [getattr(lead, field) for field in fields]
                writer.writerow(row)  # Write each row with the object's attribute values

            return response
    if "platform-option" in request.GET:
        job_ids = request.GET['jobs'].split(",")
        job_ids = [int(x) for x in job_ids if x != '']
        print(job_ids)
        if request.GET['search']:
            query = request.GET['search']

            leads = Job.objects.filter(keword__icontains=query)
            leads = leads.filter(task_id__in=job_ids)
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(company_email="-"))
                    leads = leads.filter(~Q(company_email=None))
                else:
                    leads = leads.filter(Q(company_email="-") or Q(company_email=None))
                    # leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(company_phone_number="-"))
                    leads = leads.filter(~Q(company_phone_number=None))
                else:
                    leads = leads.filter(Q(company_phone_number="-") or Q(company_phone_number=None))
                    # leads = leads.filter(phone_number="NA")
            if request.GET['platform-option']!="All Platforms":
                if " and " in request.GET['platform-option']:
                    leads = leads.filter(
                        Q(source_website__icontains=request.GET['platform-option'].split(" and ")[0]) | Q(
                            source_website__icontains=request.GET['platform-option'].split(" and ")[1]))
                else:
                    leads = leads.filter(source_website__icontains=request.GET['platform-option'])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Jobs-export.csv"'

            writer = csv.writer(response)

            # Get all fields of the Lead model
            fields = [field.name for field in Job._meta.get_fields()]

            writer.writerow(fields)  # Write header row

            for lead in leads:
                row = [getattr(lead, field) for field in fields]
                writer.writerow(row)  # Write each row with the object's attribute values

            return response

        else:
            query = ""
            leads = Job.objects.all()
            leads = leads.filter(task_id__in=job_ids)
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(company_email="-"))
                    leads = leads.filter(~Q(company_email=None))
                else:
                    leads = leads.filter(Q(company_email="-") or Q(company_email=None))
                    # leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(company_phone_number="-"))
                    leads = leads.filter(~Q(company_phone_number=None))
                else:
                    leads = leads.filter(Q(company_phone_number="-") or Q(company_phone_number=None))
                    # leads = leads.filter(phone_number="NA")
            if request.GET['platform-option'] != "All Platforms":
                if " and " in request.GET['platform-option']:
                    leads = leads.filter(
                        Q(source_website__icontains=request.GET['platform-option'].split(" and ")[0]) | Q(
                            source_website__icontains=request.GET['platform-option'].split(" and ")[1]))
                else:
                    leads = leads.filter(source_website__icontains=request.GET['platform-option'])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Jobs-export.csv"'

            writer = csv.writer(response)

            # Get all fields of the Lead model
            fields = [field.name for field in Job._meta.get_fields()]

            writer.writerow(fields)  # Write header row

            for lead in leads:
                row = [getattr(lead, field) for field in fields]
                writer.writerow(row)  # Write each row with the object's attribute values

            return response
def search_lead(request):
    try:
        pg_num = request.GET['page']
    except:
        pg_num = 1
    if 'size-option' in request.GET:
        if request.GET['search']:
            query=request.GET['search']


            leads = Leads.objects.filter(title__icontains=query)
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option']=="With emails":
                    leads=leads.filter(~Q(email=None))
                    leads = leads.filter(~Q(email="NA"))
                else:
                    leads=leads.filter(email=None)
                    leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option']=="With Phone No.":
                    leads=leads.filter(~Q(phone_number=None))
                    leads = leads.filter(~Q(phone_number="NA"))
                else:
                    leads=leads.filter(phone_number=None)
                    leads = leads.filter(phone_number="NA")
            if request.GET['size-option']:
                leads = leads.filter(employees__icontains=request.GET['size-option'])
            paginator = Paginator(leads, 70)
            page_obj = paginator.get_page(pg_num)
        else:
            query=""
            leads = Leads.objects.all()
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(email=None))
                    leads = leads.filter(~Q(email="NA"))
                else:
                    leads = leads.filter(Q(email=None) or Q(email="NA"))
                    # leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(phone_number=None))
                    leads = leads.filter(~Q(phone_number="NA"))
                else:
                    leads = leads.filter(Q(phone_number=None) or Q(phone_number="NA"))
                    # leads = leads.filter(phone_number="NA")
            if request.GET['size-option']:
                leads = leads.filter(employees__icontains=request.GET['size-option'])
            paginator = Paginator(leads, 70)
            page_obj = paginator.get_page(pg_num)

        return render(request,"page1.html",{'page_obj':page_obj,'query':query,"email_option":request.GET['email-option'],
                                            "number_option":request.GET['number-option'],"size_option":request.GET['size-option']})
    if 'platform-option' in request.GET:
        job_ids=request.GET['jobs'].split(",")
        job_ids = [int(x) for x in job_ids if x != '']
        print(job_ids)
        if request.GET['search']:

            query = request.GET['search']

            leads = Job.objects.filter(keword__icontains=query)
            leads=leads.filter(task_id__in=job_ids)
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(company_email="-"))
                    leads = leads.filter(~Q(company_email=None))
                else:
                    leads = leads.filter(company_email="-")
                    leads = leads.filter(company_email=None)
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(company_phone_number="-"))
                    leads = leads.filter(~Q(company_phone_number=None))
                else:
                    leads = leads.filter(company_phone_number="-")
                    leads = leads.filter(company_phone_number=None)
            if request.GET['platform-option']!="All Platforms":
                if " and " in request.GET['platform-option']:
                    leads = leads.filter(
                        Q(source_website__icontains=request.GET['platform-option'].split(" and ")[0]) | Q(
                            source_website__icontains=request.GET['platform-option'].split(" and ")[1]))
                else:
                    leads = leads.filter(source_website__icontains=request.GET['platform-option'])
            paginator = Paginator(leads, 70)
            page_obj = paginator.get_page(pg_num)
        else:
            query = ""
            leads = Job.objects.all()
            leads = leads.filter(task_id__in=job_ids)
            if request.GET['email-option'] != "Show All":
                if request.GET['email-option'] == "With emails":
                    leads = leads.filter(~Q(company_email="-"))
                    leads = leads.filter(~Q(company_email=None))
                else:
                    leads = leads.filter(Q(company_email=None) or Q(company_email="NA"))
                    # leads = leads.filter(email="NA")
            if request.GET['number-option'] != "Show All":
                if request.GET['number-option'] == "With Phone No.":
                    leads = leads.filter(~Q(company_phone_number="-"))
                    leads = leads.filter(~Q(company_phone_number=None))
                else:
                    leads = leads.filter(Q(company_phone_number="-") or Q(company_phone_number=None))
                    # leads = leads.filter(phone_number="NA")
            if request.GET['platform-option']!="All Platforms":
                if " and " in request.GET['platform-option']:
                    leads = leads.filter(
                        Q(source_website__icontains=request.GET['platform-option'].split(" and ")[0]) | Q(source_website__icontains=request.GET['platform-option'].split(" and ")[1]))
                else:
                    leads = leads.filter(source_website__icontains=request.GET['platform-option'])
            paginator = Paginator(leads, 70)
            page_obj = paginator.get_page(pg_num)

        return render(request, "jobs.html",
                      {'page_obj': page_obj, 'query': query, "email_option": request.GET['email-option'],
                       "number_option": request.GET['number-option'], "platform_option": request.GET['platform-option'],"job_tasks":job_ids,
                       "data_length":len(list(leads))})


def view_lead(request):
    lead_id=request.GET['lead']
    Lead = Leads.objects.get(id=lead_id)
    return render(request,"edit.html",{"lead":Lead})
def view_job(request):
    lead_id=request.GET['job']
    Lead = Job.objects.get(id=lead_id)
    return render(request,"job_edit.html",{"lead":Lead})
@csrf_exempt
def dashboard(request):
    filters=open("filters.json","r").read()
    filters=json.loads(filters)

    try:
        pg_num=request.GET['page']
    except:
        pg_num=1
    data=get_all(request,pg_num)

    if request.user.is_authenticated:
        data = get_all(request, pg_num)
        return render(request,'page1.html',{"page_obj":data})
    else:
        return render(request, 'index.html')
@csrf_exempt
def jobs(request):
    print(request.GET.urlencode())
    job_ids=request.GET.urlencode().split("&page=")[0].replace("&",",").replace("=on","").split(",")
    job_ids = [int(x) for x in job_ids]

    try:
        pg_num=request.GET['page']
    except:
        pg_num=1
    # data=get_all_jobs(request,pg_num,job_ids)

    if request.user.is_authenticated:
        data,lent = get_all_jobs(request, pg_num,job_ids)
        return render(request,'jobs.html',{"page_obj":data,"job_tasks":request.GET.urlencode().replace("&",",").replace("=on","").split(","),
                                           "job_page_change":request.GET.urlencode(),"data_length":lent})
    else:
        return render(request, 'jobs.html')
@csrf_exempt
def create_Lead(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Lead = Leads.objects.create(
            title=data['title'],
            author=data['author'],
            published_date=data['published_date']
        )
        return JsonResponse({'id': Lead.id})
    return JsonResponse({'error': 'Invalid request method'})

# Read
def get_Lead(request, id):
    try:
        Lead = Leads.objects.get(id=id)
        return JsonResponse({
            'id': Lead.id,
            'title': Lead.title,
            'author': Lead.author,
            'published_date': Lead.published_date
        })
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'})
def task(request):

    if request.method=="POST":
        print("Task")
        navigator_link=request.POST['navigator_link']
        no_of_leads = request.POST['no_of_leads']
        friendly_name=request.POST['friendly_name']
        status="pending"
        obj=Task.objects.create(navigator_link=navigator_link,no_of_leads=no_of_leads,status=status,friendly_name=friendly_name)
        obj.save()

    page_number=1
    task = Task.objects.all()
    # page_number = request.GET.get('page')  or 1
    paginator = Paginator(task, 70)
    page_obj = paginator.get_page(page_number)

    return render(request,"page2.html",{"page_obj":page_obj})
# Update
@csrf_exempt
def update_Lead(request):
    if request.method == 'POST':
        id=request.POST['lead_id']
        try:
            Lead = Leads.objects.get(id=id)
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'})
        data = request.POST
        Lead.first_name = data['first_name']
        Lead.last_name = data['last_name']
        Lead.title = data['title']
        Lead.email = data['email']
        Lead.phone_number = data['phone']
        Lead.company_name = data['company_name']
        Lead.company_website = data['company_website']
        Lead.save()
        return redirect(dashboard)
        # return JsonResponse({'message': 'Lead updated successfully'})
    return JsonResponse({'error': 'Invalid request method'})
def update_job(request):
    if request.method == 'POST':
        id=request.POST['lead_id']
        try:
            job = Job.objects.get(id=id)
        except job.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'})
        data = request.POST
        job.keword = data['keyword']
        job.Job_title = data['Job Title']
        job.company_name = data['Company Name']
        job.company_website = data['Company Website']
        job.source_Website = data['Source Website']
        job.company_email = data['Company Email']
        job.description = data['Description']
        job.company_phone_number = data['Company Phone Number']
        job.source_link = data['Source Link']
        job.location = data['location']
        job.save()
        return redirect(jobs)
        # return JsonResponse({'message': 'Lead updated successfully'})
    return JsonResponse({'error': 'Invalid request method'})
# Delete
@csrf_exempt
def delete_Lead(request, id):
    try:
        Lead = Leads.objects.get(id=id)
        Lead.delete()
        return JsonResponse({'message': 'Lead deleted successfully'})
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'})


def get_all(request,page_number=1):
    leads = Leads.objects.all()
    # page_number = request.GET.get('page')  or 1
    paginator = Paginator(leads, 20)
    page_obj = paginator.get_page(page_number)
    print(page_obj.has_previous())
    for i in page_obj:
        print(i)
    page_data = serializers.serialize('json', page_obj)
    return page_obj

def get_all_jobs(request,page_number=1,job_ids=[]):
    print(job_ids,"=jjns")
    leads = Job.objects.all().order_by('-id').filter(task_id__in=job_ids)
    # page_number = request.GET.get('page')  or 1
    paginator = Paginator(leads, 20)
    page_obj = paginator.get_page(page_number)

    # for i in page_obj:
    #     print(i)
    page_data = serializers.serialize('json', page_obj)
    return page_obj,len(list(leads))

@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):
    if created:
        if "job" not in instance.navigator_link:
            # Do something with the newly created task object
            print(f"New task created with id: {instance.id}")
            with open("tool/bot/settings.txt", "r") as file:
                lines = file.readlines()
                linkedin_email = lines[0].replace("\n", "")
                linkedin_pass = lines[1].replace("\n", "")
                print(linkedin_email)
                print(linkedin_pass)


            # get existing data

            existing_data = [link for (link,) in Leads.objects.values_list('linkedin')]
            # do_thread(existing_data, linkedin_email, linkedin_pass, instance.no_of_leads, instance.navigator_link)
            s=threading.Thread(target=do_thread,args=(existing_data, linkedin_email, linkedin_pass, instance.no_of_leads, instance.navigator_link,
                                                      instance.id,"lead"))
            s.start()


def update_status(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        job_id = request.POST.get('job_id')
        status = request.POST.get('status')

        try:
            job_task = JobTask.objects.get(id=job_id)
            job_task.status = status
            job_task.save()

            return JsonResponse({'success': True})
        except JobTask.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job task not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def get_updated_counts(request, job_id):
    try:
        linkedin = Job.objects.filter(task_id=job_id,source_website="Linkedin")
        glassdoor = Job.objects.filter(task_id=job_id, source_website="GlassDoor")
        indeed = Job.objects.filter(task_id=job_id, source_website="Indeed")
    except Exception as e:
        print(e)
        pass

    # Retrieve the counts for the job
    linkedin_count = len(list(linkedin))
    glassdoor_count = len(list(glassdoor))
    indeed_count = len(list(indeed))

    # Return the counts as a JSON response
    return JsonResponse({
        'linkedin_count': linkedin_count,
        'glassdoor_count': glassdoor_count,
        'indeed_count': indeed_count,
    })



post_save.connect(task_created, sender=Task)



