from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    path('Leads/', create_Lead, name='create_Lead'),
    path('Leads/<int:Lead_id>/', get_Lead, name='get_Lead'),
    path('update_Leads', update_Lead, name='update_Lead'),
    path('Leads/<int:Lead_id>/', delete_Lead, name='delete_Lead'),
    path('Leads/all/', get_all, name='get_all'),
    path('', dashboard, name='dashboard'),
path('apply_export', apply_export, name='apply_export'),
path('view_lead', view_lead, name='view_lead'),
path('view_job', view_job, name='view_job'),
path('update_job', update_job, name='update_job'),
path('task', task, name='task'),
path('login', login, name='login'),
path('jobs', jobs, name='jobs'),
path('logout', logoutt, name='logout'),
path('search', search_lead, name='search_lead'),
path('export', export, name='export'),
path('get_job_email', get_job_email, name='get_job_email'),
path('jobs_task', jobs_task, name='jobs_task'),
path('update_status',update_status,name='update_status'),
path('get-updated-counts/<int:job_id>/', get_updated_counts, name='get_updated_counts'),
]
