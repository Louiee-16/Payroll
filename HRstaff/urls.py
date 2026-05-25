from django.urls import path
from . import views
urlpatterns = [
    path('HR/dashboard/',views.HR_dashboard, name='HR-DASHBOARD'),
    ######### sidebuttons
    path('HR/teams',views.TEAM, name='SIDEBUTTON-TEAM'),
    path('HR/logins',views.LOGINS, name='SIDEBUTTON-LOGINS'),
    path('HR/time_tracking',views.TIME_TRACKING, name='SIDEBUTTON-TIME-TRACKING'),
    path('HR/add_employee',views.ADD_EMPLOYEE, name='SIDEBUTTON-ADD-EMPLOYEE'),
]
