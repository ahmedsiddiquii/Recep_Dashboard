from django.contrib import admin
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Leads,Task,Job,JobTask

class LeadAdmin(admin.ModelAdmin):
    pass
class TaskAdmin(admin.ModelAdmin):
    pass
class JobAdmin(admin.ModelAdmin):
    pass

class JobTaskAdmin(admin.ModelAdmin):
    pass

admin.site.register(Leads, LeadAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Job, TaskAdmin)
admin.site.register(JobTask, JobTaskAdmin)