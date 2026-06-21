import datetime

from django.db import models
from django.utils import timezone

from employees.models import Employees


class Attendance(models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='attendance_logs')
    date     = models.DateField(auto_now_add=True)
    time_in  = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.first_name} - {self.date}"

    @property
    def is_late(self):
        if self.time_in and self.employee.duty_in:
            local = timezone.localtime(self.time_in)
            return local.time() > self.employee.duty_in
        return False

    @property
    def late_minutes(self):
        if not self.is_late:
            return 0
        local = timezone.localtime(self.time_in)
        duty_dt  = datetime.datetime.combine(local.date(), self.employee.duty_in)
        check_dt = datetime.datetime.combine(local.date(), local.time())
        return int((check_dt - duty_dt).total_seconds() // 60)

    @property
    def hours_worked(self):
        if self.time_in and self.time_out:
            delta = self.time_out - self.time_in
            return round(delta.total_seconds() / 3600, 1)
        return None
