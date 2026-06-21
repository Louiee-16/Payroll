from django.db import models
from user.models import User
from datetime import time
class Employees(models.Model):
    STATUS_CHOICES = [
        ('PERMANENT', 'Permanent'),
        ('CONTRACTUAL', 'Contractual'),
    ]
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    email_address = models.EmailField(max_length=50)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=250)
    degree = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    RFID = models.CharField(max_length=50, null=True, blank=True)
    bank = models.CharField(max_length=50, null=True, blank=True)
    basic_pay = models.DecimalField(max_digits=12, decimal_places=2)
    date_hired = models.DateField(auto_now_add=True)
    on_leave = models.BooleanField(default=False)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PERMANENT')
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account')
    employee_id = models.CharField(max_length=50, default='0')
    duty_in = models.TimeField(default=time(7, 0))
    duty_out = models.TimeField(default=time(5, 0))
    is_archive = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.employee_id})"


