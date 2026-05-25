from django.urls import path
from . import views
urlpatterns = [
    path('employee/add',views.add_employee, name='ADD-EMPLOYEE'),
    path('employee/',views.employee_dashboard, name='EMPLOYEE-DASHBOARD'),
    path('employee/leave',views.employee_leave, name='EMPLOYEE-LEAVE'),
    path('employee/file/leave', views.file_leave, name="FILE-LEAVE"),
    path('employee/DTR',views.DTR, name="DTR"),
]
