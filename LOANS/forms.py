from django import forms
from .models import loans

class Loan_form(forms.ModelForm):
    class Meta:
        model = loans
        fields = []  # leave empty because we set fields manually