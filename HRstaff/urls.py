from django.urls import path
from . import views
urlpatterns = [
    path('HR/dashboard/',views.HR_dashboard, name='HR-DASHBOARD'),
    ######### sidebuttons
    path('HR/teams',views.TEAM, name='SIDEBUTTON-TEAM'),
    path('HR/logins',views.LOGINS, name='SIDEBUTTON-LOGINS'),
    path('HR/time_tracking',views.TIME_TRACKING, name='SIDEBUTTON-TIME-TRACKING'),
    path('HR/add_employee',views.ADD_EMPLOYEE, name='SIDEBUTTON-ADD-EMPLOYEE'),

    path('HR/archive/<int:id>/',views.ARCHIVE, name='ARCHIVE'),
    path('HR/employee/<int:emp_id>/', views.employee_profile, name='EMPLOYEE-PROFILE'),
    path('HR/employee/<int:emp_id>/edit/', views.edit_employee, name='EDIT-EMPLOYEE'),
    path('HR/employee/<int:emp_id>/reset-password/', views.reset_employee_password, name='RESET-PASSWORD'),
    path('HR/search/', views.search_employees, name='SEARCH-EMPLOYEES'),
]
