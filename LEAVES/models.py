from django.db import models
from employees.models import Employees


LEAVE_BALANCE_FIELD = {
    'VACATION':     'vacation',
    'SICK':         'sick',
    'SPL':          'spl',
    'SOLO_PARENT':  'solo_parent',
    'MATERNITY':    'maternity',
    'PATERNITY':    'paternity',
}


class LeaveBalance(models.Model):
    employee = models.OneToOneField(Employees, on_delete=models.CASCADE, related_name='leave_balance')

    vacation    = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    sick        = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    spl         = models.DecimalField(max_digits=5, decimal_places=2, default=3)
    solo_parent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    maternity   = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    paternity   = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def get_balance(self, leave_type):
        field = LEAVE_BALANCE_FIELD.get(leave_type)
        return getattr(self, field, 0) if field else 0

    def deduct(self, leave_type, days):
        field = LEAVE_BALANCE_FIELD.get(leave_type)
        if field:
            current = getattr(self, field)
            setattr(self, field, current - days)
            self.save()

    def __str__(self):
        return f"{self.employee} — VL:{self.vacation} SL:{self.sick} SPL:{self.spl}"


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    LEAVE_TYPES = [
        ('VACATION',     'Vacation Leave'),
        ('SICK',         'Sick Leave'),
        ('SPL',          'Special Privilege Leave'),
        ('SOLO_PARENT',  'Solo Parent Leave'),
        ('MATERNITY',    'Maternity Leave'),
        ('PATERNITY',    'Paternity Leave'),
    ]

    employee    = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='leaves')
    leave_type  = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date  = models.DateField(null=True, blank=True)
    end_date    = models.DateField(null=True, blank=True)
    reason      = models.TextField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __str__(self):
        return f"{self.employee.first_name} - {self.get_leave_type_display()}"


class LeaveHistory(models.Model):
    employee     = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='leave_history')
    leave_type   = models.CharField(max_length=20)
    start_date   = models.DateField(null=True, blank=True)
    end_date     = models.DateField(null=True, blank=True)
    reason       = models.TextField()
    status       = models.CharField(max_length=10, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    duration     = models.IntegerField(null=True, blank=True)
