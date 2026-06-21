from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
        ('EMPLOYEE', 'Employee'),

    )
    role = models.CharField(max_length=20, choices=ROLES, default='STAFF')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Notification(models.Model):
    TYPES = [
        ('LEAVE_APPROVED',  'Leave Approved'),
        ('LEAVE_REJECTED',  'Leave Rejected'),
        ('LEAVE_FILED',     'Leave Filed'),
        ('LEAVE_CREDITED',  'Leave Credited'),
        ('PASSWORD_RESET',  'Password Reset'),
    ]

    recipient         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type  = models.CharField(max_length=20, choices=TYPES)
    message           = models.CharField(max_length=255)
    link              = models.CharField(max_length=255, blank=True, default='')
    is_read           = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.message[:50]}"


class AuditLog(models.Model):
    ACTION_TYPES = [
        ('LOGIN',            'Login'),
        ('LOGOUT',           'Logout'),
        ('EMPLOYEE_CREATED', 'Employee Created'),
        ('EMPLOYEE_EDITED',  'Employee Edited'),
        ('EMPLOYEE_ARCHIVED','Employee Archived'),
        ('SALARY_CHANGED',   'Salary Changed'),
        ('LEAVE_APPROVED',   'Leave Approved'),
        ('LEAVE_REJECTED',   'Leave Rejected'),
        ('LEAVE_FILED',      'Leave Filed'),
        ('LEAVE_CREDITED',   'Leave Credited'),
        ('PASSWORD_RESET',   'Password Reset'),
        ('PASSWORD_CHANGED', 'Password Changed'),
        ('PAYROLL_LOCKED',   'Payroll Locked'),
        ('LOAN_UPDATED',     'Loan Updated'),
        ('ADJUSTMENT_ADDED', 'Adjustment Added'),
    ]

    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action      = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.CharField(max_length=500)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.action}] {self.user} - {self.description[:60]}"


def log_action(request, action, description):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        description=description,
        ip_address=ip or None,
    )