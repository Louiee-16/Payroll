from django.db import models
from employees.models import Employees
# Create your models here.
class Attendance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='attendance_logs')
    
    date = models.DateField(auto_now_add=True) 
    
    
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.first_name} - {self.date}"