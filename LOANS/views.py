from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from employees.models import Employees
from user.decorators import staff_required
from user.models import log_action

from .forms import Loan_form
from .models import loans


def _safe_float(val):
    return float(val) if val is not None else 0.0


@staff_required
def LOAN(request):
    form = Loan_form()
    employees = Employees.objects.all()
    return render(request, 'sidebuttons/loan.html', {'form': form, 'employees': employees})


@staff_required
def monthly_payment(request, emp_id):
    try:
        employee = get_object_or_404(Employees, id=emp_id)
        loan_record = employee.employee_loans.first()

        if not loan_record:
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
                "take_home": float(employee.basic_pay),
            }
        else:
            data = {
                "id": employee.id,
                "SSS_salary_monthly": _safe_float(loan_record.SSS_salary_monthly),
                "SSS_calamity_monthly": _safe_float(loan_record.SSS_calamity_monthly),
                "SSS_MPL_monthly": _safe_float(loan_record.SSS_MPL_monthly),
                "SSS_educ_monthly": _safe_float(loan_record.SSS_educ_monthly),
                "PAGIBIG_MPL_monthly": _safe_float(loan_record.PAGIBIG_MPL_monthly),
                "PAGIBIG_housing_monthly": _safe_float(loan_record.PAGIBIG_housing_monthly),
                "COOP_monthly": _safe_float(loan_record.COOP_monthly),
                "total_loans": _safe_float(loan_record.total_loans),
                "total_monthly": _safe_float(loan_record.monthly_deductions),
                "take_home": _safe_float(employee.basic_pay - loan_record.monthly_deductions),
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@staff_required
def employee_loans(request, emp_id):
    try:
        employee = get_object_or_404(Employees, id=emp_id)
        loan_record = employee.employee_loans.first()

        if not loan_record:
            data = {
                "id": employee.id,
                "SSS_salary": 0.0, "SSS_calamity": 0.0, "SSS_MPL": 0.0, "SSS_educ": 0.0,
                "PAGIBIG_MPL": 0.0, "PAGIBIG_housing": 0.0, "COOP": 0.0,
                "total_loans": 0.0, "total_monthly": 0.0,
            }
        else:
            data = {
                "id": employee.id,
                "SSS_salary": _safe_float(loan_record.SSS_salary),
                "SSS_calamity": _safe_float(loan_record.SSS_calamity),
                "SSS_MPL": _safe_float(loan_record.SSS_MPL),
                "SSS_educ": _safe_float(loan_record.SSS_educ),
                "PAGIBIG_MPL": _safe_float(loan_record.PAGIBIG_MPL),
                "PAGIBIG_housing": _safe_float(loan_record.PAGIBIG_housing),
                "COOP": _safe_float(loan_record.COOP),
                "total_loans": _safe_float(loan_record.total_loans),
                "total_monthly": _safe_float(loan_record.monthly_deductions),
                "take_home": _safe_float(employee.basic_pay - loan_record.monthly_deductions),
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@staff_required
def Input_loans(request):
    if request.method == "POST":
        emp_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employees, id=emp_id)

        loan_instance, _ = loans.objects.get_or_create(employee=employee)

        selected = request.POST.get('loanType')
        if selected:
            amount = request.POST.get('total_amount') or 0
            monthly = request.POST.get('monthly') or 0
            setattr(loan_instance, selected, amount)
            setattr(loan_instance, f"{selected}_monthly", monthly)
            loan_instance.save()
            log_action(request, 'LOAN_UPDATED', f'Updated {selected} loan for {employee.first_name} {employee.last_name}: total={amount}, monthly={monthly}.')

    return redirect('SIDEBUTTON-LOAN')
