from django.urls import path
from . import views

app_name = 'adminPanel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban-user/<int:user_id>/', views.unban_user, name='unban_user'),
    path('messages/', views.message_management, name='messages'),
    path('messages/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]