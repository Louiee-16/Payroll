from django import forms
from .models import Employees


class add_employee_form(forms.ModelForm):
    class Meta:
        model = Employees
        fields = [
            'last_name', 'first_name', 'email_address', 'mobile_number',
            'address', 'degree', 'designation', 'department',
            'RFID', 'bank', 'basic_pay',
        ]


class EditEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = [
            'last_name', 'first_name', 'email_address', 'mobile_number',
            'address', 'degree', 'designation', 'department',
            'RFID', 'bank', 'basic_pay', 'status', 'duty_in', 'duty_out',
        ]
        widgets = {
            'duty_in':  forms.TimeInput(attrs={'type': 'time'}),
            'duty_out': forms.TimeInput(attrs={'type': 'time'}),
        }
