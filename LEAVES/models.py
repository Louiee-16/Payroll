from django.db import models
from employees.models import Employees

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    LEAVE_TYPES = [
        ('SICK', 'Sick Leave'),
        ('VACATION', 'Vacation'),
        ('EMERGENCY', 'Emergency'),
        ('MATERNITY', 'Maternity/Paternity'),
    ]

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField(null=True, blank =True)
    end_date = models.DateField(null=True, blank =True)
    sick_leave = models.DecimalField(max_digits=5,decimal_places=2, default=0)
    vacation_leave = models.DecimalField(max_digits=5,decimal_places=2, default=0)
    SPL = models.DecimalField(max_digits=5,decimal_places=2, default=0)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    

    @property
    def duration(self):
        return (self.end_date - self.start_date).days + 1
            

    def __str__(self):
        return f"{self.employee.first_name} - {self.leave_type}"
    

class LeaveHistory(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='employee' )
    leave_type = models.CharField(max_length=20)
    start_date = models.DateField(null=True, blank =True)
    end_date = models.DateField(null=True, blank =True)
    reason = models.TextField()
    status = models.CharField(max_length=10, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(null=True, blank=True)