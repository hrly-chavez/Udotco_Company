from django.urls import path
from . import views

app_name = 'driver'
urlpatterns = [
    path('driver/', views.driver_request, name='driver_request'),
    path('add_request/', views.add_request, name='add_request'),
    path('logout/', views.logout_view, name='logout'),
]
