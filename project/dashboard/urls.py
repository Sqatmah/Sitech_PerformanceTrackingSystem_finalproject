from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('export/students/', views.export_students, name='export_students'),
    path('export/assignments/', views.export_assignments, name='export_assignments'),
    path('stats/', views.dashboard_stats, name='stats'),
]