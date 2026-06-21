from django.urls import path
from . import views

urlpatterns = [
    path('admin/dashboard/', views.Admin_dashboard, name='admin-dashboard'),
    path('notifications/', views.notifications_page, name='NOTIFICATIONS'),
    path('notifications/mark-read/<int:notif_id>/', views.mark_notification_read, name='MARK-NOTIFICATION-READ'),
    path('notifications/mark-all-read/', views.mark_all_read, name='MARK-ALL-READ'),
    path('audit-log/', views.audit_log_page, name='AUDIT-LOG'),
]
