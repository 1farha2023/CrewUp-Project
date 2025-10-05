from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('detail/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('create/', views.campaign_create, name='campaign_create'),
    path('edit/<int:campaign_id>/', views.campaign_update, name='campaign_update'),
    path('delete/<int:campaign_id>/', views.campaign_delete, name='campaign_delete'),

    # Influencer-specific URLs
    path('apply/<int:campaign_id>/', views.apply_to_campaign, name='apply_to_campaign'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('analytics/', views.influencer_analytics, name='influencer_analytics'),

    # Application management URLs
    path('applications/<int:application_id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),
    path('campaign/<int:campaign_id>/applications/', views.brand_campaign_applications, name='brand_campaign_applications'),
]