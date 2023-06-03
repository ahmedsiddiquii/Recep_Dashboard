from django.db import models
from django.db import models
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

# Create your models here.




class Leads(models.Model):
    name = models.CharField(max_length=100, default=None)
    last_name = models.CharField(max_length=100,default=None)
    first_name = models.CharField(max_length=100,default=None)
    title = models.CharField(max_length=100, default=None,null=True)
    email = models.CharField(max_length=100, default=None,null=True)
    phone_number = models.CharField(max_length=100, default=None,null=True)
    linkedin = models.CharField(max_length=400, default=None,null=True)
    employees = models.CharField(max_length=100, default=None,null=True)
    company_website = models.CharField(max_length=100, default=None,null=True)
    company_name = models.CharField(max_length=100, default=None,null=True)
    location = models.CharField(max_length=100, default=None,null=True)
    linkedin_sales_navigator = models.CharField(max_length=500, default=None,null=True)
class Task(models.Model):
    navigator_link = models.CharField(max_length=1000, default=None)
    no_of_leads = models.CharField(max_length=100, default=None)
    status = models.CharField(max_length=100, default=None)
    friendly_name=models.CharField(max_length=100, default=None,null=True)

class JobTask(models.Model):
    linkedin_link = models.CharField(max_length=1000, default=None,null=True)
    indeed_link = models.CharField(max_length=1000, default=None,null=True)
    glassdoor_link = models.CharField(max_length=1000, default=None,null=True)
    friendly_name = models.CharField(max_length=100, default=None)
    status = models.CharField(max_length=100, default=None)
    last_updated = models.DateTimeField(null=True)
    next_update = models.DateTimeField(null=True)
    activity_status= models.CharField(max_length=100, default=None,null=True)

class Job(models.Model):
    keword=models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    location = models.CharField(max_length=100,null=True)
    company_name = models.CharField(max_length=100)
    company_website = models.URLField(null=True)
    description = models.TextField()
    source_link= models.CharField(max_length=100)
    source_website = models.URLField(null=True)
    company_email=models.CharField(max_length=100)
    company_phone_number=models.CharField(max_length=100)
    task_id=models.IntegerField(null=True)
    def __str__(self):
        return self.job_title

