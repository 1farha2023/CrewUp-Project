"""
URL configuration for crewup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('pricing/', views.pricing, name='pricing'),
    path('success-stories/', views.success_stories, name='success_stories'),
    path('brands/', views.brands, name='brands'),
    path('influencers/', views.influencers, name='influencers'),
    path('influencer/<int:influencer_id>/', views.influencer_profile, name='influencer_profile'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('campaigns/', include('campaigns.urls')),
    path('auth/', include('authentication.urls')),
    path('payment/', include('payments.urls')),
    path('admin-dashboard/', include('adminPanel.urls', namespace='adminPanel')),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('influencer-dashboard/', views.influencer_dashboard, name='influencer_dashboard'),
    path('brand-dashboard/', views.brand_dashboard, name='brand_dashboard'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else '')
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
