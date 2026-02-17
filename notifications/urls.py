from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'notifications'

urlpatterns = [
    # ==================== نظام الإشعارات ====================
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<uuid:notification_id>/delete/', views.delete_notification, name='delete_notification'),
]