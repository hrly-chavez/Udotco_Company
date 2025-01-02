from django.urls import path
from . import views


app_name = 'mechanic'

urlpatterns = [
    path( '', views.joborder_list, name='joborder_list'),
    path('joborder-list/', views.joborder_list, name='joborder_list'),
    path('update-job-status/', views.update_job_status, name='update_job_status'),
    path('logout/', views.logout_view, name='logout'),
    path('inventory/', views.inventory, name='inventory'),
    path('create_item_req/<int:job_order_id>/', views.create_item_req, name='create_item_req'),
    path('view_item_requests/', views.view_item_requests, name='view_req'),
    path('fetch_materials/', views.fetch_materials, name='fetch_materials'),



]
