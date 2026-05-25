from django.urls import path
from . import views

urlpatterns = [
    path('loan/',views.LOAN,name='SIDEBUTTON-LOAN'),
    path("loans/<int:emp_id>/monthly_payment/",views.monthly_payment, name='MONTHLY-PAYMENT'),
    path("loans/<int:emp_id>/",views.employee_loans, name='EMPLOYEE_LOANS'),
    path("loans/add/",views.Input_loans, name = "INPUT-LOAN"),
    
]
