from django.urls import path
from . import views

app_name = 'adminPanel'

urlpatterns = [
    path('', views.dashboard_view, name='admin-dashboard'),
]