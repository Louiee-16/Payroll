from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from employees.models import Employees

@login_required
def HR_dashboard(request):
    if request.user.role != "STAFF":
        return redirect('login') 
    employees = Employees.objects.all()
    on_leave = Employees.objects.filter(on_leave=True).count()
    new = Employees.objects.filter(status = 'New').count()
    contractuals = Employees.objects.filter(status = 'CONTRACTUAL')

    context = {
        'employees' : employees,
        'on_leave': on_leave,
        'new' : new,
        'contractuals' : contractuals,

    }
    return render(request, 'dashboards/HR_dashboard.html',context)

#SIDE BUTTONS
@login_required
def TEAM(request):
    employees = Employees.objects.all()
    on_leave = Employees.objects.filter(on_leave=True).count()
    new = Employees.objects.filter(status = 'New').count()
    contractuals = Employees.objects.filter(status = 'CONTRACTUAL')

    context = {
        'employees' : employees,
        'on_leave': on_leave,
        'new' : new,
        'contractuals' : contractuals,

    }
    return render(request, 'sidebuttons/teams.html',context)

@login_required
def ONBOARD(request):
    return render(request,'sidebuttons/onboard.html')



@login_required
def LOGINS(request):
    return render(request,'sidebuttons/logs.html')


@login_required
def TIME_TRACKING(request):
    return render(request,'sidebuttons/time_tracking.html')


@login_required
def ADD_EMPLOYEE(request):
    return render(request,'sidebuttons/add_employee.html')


