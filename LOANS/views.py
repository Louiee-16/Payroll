from django.shortcuts import render,redirect, get_object_or_404
from employees.models import Employees
from django.http import JsonResponse
from . models import loans
from django.http import JsonResponse, Http404
from django.db.models.functions import Coalesce
from django.db.models import F, Sum
from .forms import Loan_form
def LOAN(request):
    form = Loan_form()

    employees = Employees.objects.all()
    context = {
        'form':form,
        'employees':employees,
    }
    return render(request, 'sidebuttons/loan.html',context)


def monthly_payment(request, emp_id):
    try:
        employee = get_object_or_404(Employees, id=emp_id)
        # Use .first() to get the record
        loan_record = employee.employee_loans.first()

        # Helper to safely convert Decimal/None to float
        def safe_float(val):
            return float(val) if val is not None else 0.0

        if not loan_record:
            # Return zeros if no record exists
            data = {
                "id": employee.id,
                "SSS_salary_monthly": 0.0,
                "SSS_calamity_monthly": 0.0,
                "SSS_MPL_monthly": 0.0,
                "SSS_educ_monthly": 0.0,
                "PAGIBIG_MPL_monthly": 0.0,
                "PAGIBIG_housing_monthly": 0.0,
                "COOP_monthly": 0.0,
                "total_loans_monthly": 0.0,
                "total_monthly": 0.0,
                "take_home": float(employee.basic_pay)  # since no deductions
            }
        else:
            data = {
                "id": employee.id,
                "SSS_salary_monthly": safe_float(loan_record.SSS_salary_monthly),
                "SSS_calamity_monthly": safe_float(loan_record.SSS_calamity_monthly),
                "SSS_MPL_monthly": safe_float(loan_record.SSS_MPL_monthly),
                "SSS_educ_monthly": safe_float(loan_record.SSS_educ_monthly),
                "PAGIBIG_MPL_monthly": safe_float(loan_record.PAGIBIG_MPL_monthly),
                "PAGIBIG_housing_monthly": safe_float(loan_record.PAGIBIG_housing_monthly),
                "COOP_monthly": safe_float(loan_record.COOP_monthly),
                "total_loans": safe_float(loan_record.total_loans),
                "total_monthly": safe_float(loan_record.monthly_deductions),
                "take_home": safe_float(employee.basic_pay - loan_record.monthly_deductions)
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
def employee_loans(request, emp_id):
    try:
        employee = get_object_or_404(Employees, id=emp_id)
        # Use .first() to get the record
        loan_record = employee.employee_loans.first()

        # Helper to safely convert Decimal/None to float
        def safe_float(val):
            return float(val) if val is not None else 0.0

        if not loan_record:
            # Return zeros if no record exists
            data = {
                "id": employee.id,
                "SSS_salary": 0.0, "SSS_calamity": 0.0, "SSS_MPL": 0.0, "SSS_educ": 0.0,
                "PAGIBIG_MPL": 0.0, "PAGIBIG_housing": 0.0, "COOP": 0.0,
                "total_loans": 0.0, "total_monthly": 0.0
            }
        else:
            data = {
                "id": employee.id,
                "SSS_salary": safe_float(loan_record.SSS_salary),
                "SSS_calamity": safe_float(loan_record.SSS_calamity),
                "SSS_MPL": safe_float(loan_record.SSS_MPL),
                "SSS_educ": safe_float(loan_record.SSS_educ),
                "PAGIBIG_MPL": safe_float(loan_record.PAGIBIG_MPL),
                "PAGIBIG_housing": safe_float(loan_record.PAGIBIG_housing),
                "COOP": safe_float(loan_record.COOP),
                # Use the calculated total_loans from your model save method
                "total_loans": safe_float(loan_record.total_loans),
                # Calculate monthly total on the fly
                "total_monthly": safe_float(loan_record.monthly_deductions),
                "take_home": safe_float(employee.basic_pay - loan_record.monthly_deductions)
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    

from django.shortcuts import get_object_or_404, redirect
from .models import loans
from employees.models import Employees
from .forms import Loan_form

def Input_loans(request):
    if request.method == "POST":
        emp_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employees, id=emp_id)

        
        loan_instance, created = loans.objects.get_or_create(employee=employee)
        sample = loan_instance.SSS_salary
        print(sample)
        selected = request.POST.get('loanType')
        if selected:
           
            amount = request.POST.get('total_amount') or 0
            monthly = request.POST.get('monthly') or 0

            setattr(loan_instance, selected, amount)
            setattr(loan_instance, f"{selected}_monthly", monthly)

            loan_instance.save()

        return redirect('SIDEBUTTON-LOAN')

    return redirect('SIDEBUTTON-LOAN')