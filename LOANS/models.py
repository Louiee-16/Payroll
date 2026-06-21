from django.db import models
from employees.models import Employees
from decimal import Decimal

class loans(models.Model):
    employee = models.ForeignKey(
        Employees, 
        on_delete=models.CASCADE, 
        related_name='employee_loans'
    )
    
    SSS_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    SSS_salary_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    SSS_calamity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    SSS_calamity_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    SSS_MPL = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    SSS_MPL_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    SSS_educ = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    SSS_educ_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    PAGIBIG_MPL = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    PAGIBIG_MPL_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    PAGIBIG_housing = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    PAGIBIG_housing_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    COOP = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    COOP_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    total_loans = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        def force_decimal(value):
            if value is None or value == "":
                return Decimal('0')
            try:
                return Decimal(str(value))
            except (ValueError, ArithmeticError):
                return Decimal('0')

        self.total_loans = sum([
            force_decimal(self.SSS_salary),
            force_decimal(self.SSS_calamity),
            force_decimal(self.SSS_MPL),
            force_decimal(self.SSS_educ),
            force_decimal(self.PAGIBIG_MPL),
            force_decimal(self.PAGIBIG_housing),
            force_decimal(self.COOP),
        ])

        self.monthly_deductions = sum([
            force_decimal(self.SSS_salary_monthly),
            force_decimal(self.SSS_calamity_monthly),
            force_decimal(self.SSS_MPL_monthly),
            force_decimal(self.SSS_educ_monthly),
            force_decimal(self.PAGIBIG_MPL_monthly),
            force_decimal(self.PAGIBIG_housing_monthly),
            force_decimal(self.COOP_monthly),
        ])

        super().save(*args, **kwargs)