from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forget-password/', views.forget_password_view, name='forget_password'),
    path('brand-profile/', views.brand_profile_view, name='brand_profile'),
    path('influencer-profile/', views.influencer_profile_view, name='influencer_profile'),
]