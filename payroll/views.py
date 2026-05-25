from django.shortcuts import render, redirect, get_object_or_404
from employees.models import Employees
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
@login_required
def PAYROLL(request):
    employees = Employees.objects.all()
    total = Employees.objects.aggregate(total = Sum('basic_pay'))
    print(total)
    context = {
        'employees':employees,
        'total':total['total']
    }
    return render(request,'sidebuttons/payroll.html',context)


def CalculateTax(request, emp_id):
    employee = get_object_or_404(Employees, id=emp_id)
    monthly = employee.basic_pay
    if (monthly <= 20833):
        tax = 0
    elif(monthly<=33333):
        tax = (monthly - 20833) * .15
    elif(monthly <=66667):
        tax = 1875 +(monthly - 33333) *.2
    elif(monthly<=166667):
        tax = 8541.80 + (monthly - 66667 )* .25
    elif(monthly <= 666667):
        tax = 183541 + (monthly - 66667) * .3
    
    sss = monthly * .05
    pagibig = 200 if (monthly * 0.2) >= 200 else monthly * 0.2

def Pagibig(request, emp_id):
    employee = get_object_or_404(Employees, id=emp_id)
    monthly = employee.basic_pay 
    pagibig = 200 if (monthly * 0.2) >= 200 else monthly * 0.2
    
def SSS(request, emp_id):
    employee = get_object_or_404(Employees, id=emp_id)
    monthly = employee.basic_pay

def Philhealth(request, emp_id):
    employee = get_object_or_404(Employees, id=emp_id)
    monthly = employee.basic_pay

def COOP(request, emp_id):
    employee = get_object_or_404(Employees, id = emp_id)
    