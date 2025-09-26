from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('detail/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
]