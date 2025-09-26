from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('forget-password/', views.forget_password_view, name='forget_password'),
]