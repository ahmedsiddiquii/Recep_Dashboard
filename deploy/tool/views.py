from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Leads,Task,Job
import json
from django.core import serializers
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import logout


from django.db.models.signals import post_save
from django.dispatch import receiver
from .scraper import do_thread
import threading
from .bot.modules.LeadGenerater import Lead_Generator
from time import sleep



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

def search_lead(request):
    query=request.GET['search']
    try:
        pg_num=request.GET['page']
    except:
        pg_num=1
    leads = Leads.objects.filter(title__icontains=query)
    paginator = Paginator(leads, 70)
    page_obj = paginator.get_page(pg_num)
    return render(request,"page1.html",{'page_obj':page_obj,'query':query})


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
    try:
        pg_num=request.GET['page']
    except:
        pg_num=1
    data=get_all_jobs(request,pg_num)

    if request.user.is_authenticated:
        data = get_all_jobs(request, pg_num)
        return render(request,'jobs.html',{"page_obj":data})
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
        status="pending"
        obj=Task.objects.create(navigator_link=navigator_link,no_of_leads=no_of_leads,status=status)
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

def get_all_jobs(request,page_number=1):
    leads = Job.objects.all().order_by('-id')
    # page_number = request.GET.get('page')  or 1
    paginator = Paginator(leads, 20)
    page_obj = paginator.get_page(page_number)
    print(page_obj.has_previous())
    for i in page_obj:
        print(i)
    page_data = serializers.serialize('json', page_obj)
    return page_obj

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
        else:

            existing_data = [link for (link,) in Leads.objects.values_list('linkedin')]
            # do_thread(existing_data, linkedin_email, linkedin_pass, instance.no_of_leads, instance.navigator_link)
            s = threading.Thread(target=do_thread, args=(
            existing_data, "linkedin_email", "linkedin_pass", int(instance.no_of_leads), instance.navigator_link,
            instance.id,"job"))
            s.start()




post_save.connect(task_created, sender=Task)



