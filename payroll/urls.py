from django.urls import path
from . import views

urlpatterns = [
    path('payroll/', views.PAYROLL, name='SIDEBUTTON-PAYROLL'),
    path('payroll/<int:emp_id>/', views.payroll_detail, name='PAYROLL-DETAIL'),
    path('payroll/download/', views.download_payroll, name='DOWNLOAD-PAYROLL'),
    path('payroll/payslip/<int:emp_id>/', views.download_payslip, name='DOWNLOAD-PAYSLIP'),
    path('payroll/lock/', views.lock_payroll, name='LOCK-PAYROLL'),
    path('payroll/history/', views.payroll_history, name='PAYROLL-HISTORY'),
    path('payroll/history/<int:run_id>/', views.payroll_history_detail, name='PAYROLL-HISTORY-DETAIL'),
    path('payroll/adjustment/', views.add_adjustment, name='ADD-ADJUSTMENT'),
]
