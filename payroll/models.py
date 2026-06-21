from django.db import models
from employees.models import Employees
from user.models import User


class PayrollRun(models.Model):
    FREQ_CHOICES = [
        ('monthly',  'Monthly'),
        ('biweekly', 'Every 2 Weeks'),
        ('weekly',   'Weekly'),
    ]

    start_date      = models.DateField()
    end_date        = models.DateField()
    frequency       = models.CharField(max_length=20, choices=FREQ_CHOICES)
    employee_count  = models.IntegerField(default=0)
    total_gross     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_net       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.start_date} - {self.end_date} ({self.get_frequency_display()})"


class PayrollPeriod(models.Model):
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='periods', null=True, blank=True)
    employee    = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='payroll_periods')

    start_date  = models.DateField()
    end_date    = models.DateField()

    days_worked  = models.IntegerField(default=0)
    absent_days  = models.IntegerField(default=0)
    late_minutes = models.IntegerField(default=0)
    leave_days   = models.IntegerField(default=0)

    gross_salary      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loan_deductions   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lwop_amount       = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    ot_hours          = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ot_pay            = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    thirteenth_month  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adjustment_total  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    first_period_pay  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    second_period_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} | {self.start_date} - {self.end_date}"


class Contribution(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    payroll  = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='contributions')

    sss_personal        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sss_employer        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sss_ec              = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    pagibig_personal    = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    pagibig_employer    = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    philhealth_personal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    philhealth_employer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax                 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coop_share          = models.DecimalField(max_digits=10, decimal_places=2, default=300)


class PayrollAdjustment(models.Model):
    TYPE_CHOICES = [
        ('BONUS',        'Bonus'),
        ('ALLOWANCE',    'Allowance'),
        ('REIMBURSEMENT','Reimbursement'),
        ('DEDUCTION',    'Deduction'),
        ('CASH_ADVANCE', 'Cash Advance'),
    ]
    EARNING_TYPES = {'BONUS', 'ALLOWANCE', 'REIMBURSEMENT'}

    employee        = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='payroll_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount          = models.DecimalField(max_digits=12, decimal_places=2)
    description     = models.CharField(max_length=200)
    effective_month = models.IntegerField()
    effective_year  = models.IntegerField()
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_earning(self):
        return self.adjustment_type in self.EARNING_TYPES

    def __str__(self):
        sign = '+' if self.is_earning else '-'
        return f"{sign}{self.amount} {self.get_adjustment_type_display()} - {self.employee}"
