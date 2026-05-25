from django.urls import path
from . import views

urlpatterns = [
    path('',views.Scan_page, name='SCAN-PAGE'),
    path('attendance/process-scan/', views.process_scan, name='PROCESS-SCAN'),

]
