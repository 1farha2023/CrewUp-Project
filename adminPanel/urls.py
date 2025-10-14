from django.urls import path
from . import views
# Create your tests here.

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'), 
    
]