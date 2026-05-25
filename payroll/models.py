from django.db import models
from employees.models import Employees

class PayrollPeriod(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    days_worked = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    late_minutes = models.IntegerField(default=0)
    leave_days = models.IntegerField(default=0)

    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    first_period_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    second_period_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

class Contribution(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    payroll = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)

    sss_personal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sss_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sss_ec = models.DecimalField(max_digits=10, decimal_places=2, default=30)

    pagibig_personal = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    pagibig_employer = models.DecimalField(max_digits=10, decimal_places=2, default=200)

    philhealth_personal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    philhealth_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    coop_share = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    
class Loan(models.Model):
    LOAN_TYPES = [
        ('SSS_SALARY', 'SSS Salary Loan'),
        ('SSS_MPL', 'SSS MPL'),
        ('SSS_CALAMITY', 'SSS Calamity'),
        ('SSS_EDUC', 'SSS Education'),
        ('PAGIBIG_HOUSING', 'Pag-IBIG Housing'),
        ('PAGIBIG_MPL', 'Pag-IBIG MPL'),
        ('COOP', 'Coop Loan'),
    ]

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    payroll = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)

    loan_type = models.CharField(max_length=50, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
