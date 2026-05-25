from django import forms
from .models import Employees

class add_employee_form(forms.ModelForm):

    last_name = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50)
    email_address = forms.EmailField(max_length=50)
    mobile_number = forms.CharField(max_length=15)
    address = forms.CharField(max_length=250)
    degree = forms.CharField(max_length=50)
    designation = forms.CharField(max_length=50)
    department = forms.CharField(max_length=50)
    RFID = forms.CharField(max_length=50)
    bank = forms.CharField(max_length=50)
    basic_pay = forms.CharField(max_length=10)

    class Meta:
        model = Employees
        fields = ['last_name','first_name','email_address','mobile_number','address','degree','designation','department','RFID','bank','basic_pay']

    