from django.db import models
from user.models import User
class Employees(models.Model):
    STATUS_CHOICES = [
        ('PERMANENT','Permanent'),
        ('CONTRACTUAL','Contractual'),
    ]
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    email_address = models.EmailField(max_length=50)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=250)
    degree = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    RFID = models.CharField(max_length=50, null=True, blank= True)
    bank = models.CharField(max_length=50, null=True, blank= True)
    basic_pay = models.IntegerField()
    date_hired = models.DateField(auto_now=True)
    on_leave = models.BooleanField(default=False)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='New')
    date_hired = models.DateField(auto_now=True)
    on_leave = models.BooleanField(default=False)
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name ='account')
    employee_id = models.CharField(max_length=50, default='0')


