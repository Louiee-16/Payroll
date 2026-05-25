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
        return f"({self.get_role_display()})"