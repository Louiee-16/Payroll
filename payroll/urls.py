from django.urls import path
from . import views

urlpatterns = [
    path('payroll/',views.PAYROLL, name='SIDEBUTTON-PAYROLL')
    
]
