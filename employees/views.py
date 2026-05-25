from django.shortcuts import render, redirect, get_object_or_404
from .forms import add_employee_form
from .models import Employees
from user.models import User
from LOANS.models import loans
from LEAVES.models import LeaveRequest, LeaveHistory
import calendar
from datetime import datetime, date
from django.shortcuts import render, get_object_or_404
from LOGS.models import Employees, Attendance
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
import datetime 

def employee_dashboard(request):
    return render(request, 'employee/employee_dashboard.html')

    
def employee_leave(request):
    emp_id = request.user.id
    
    employee = get_object_or_404(Employees, account=emp_id)
    
    history = LeaveHistory.objects.filter(employee=employee).order_by('-requested_at')

    context = {
        'employee': employee,
        'history': history,
        'today': datetime.date.today().strftime('%Y-%m-%d')
    }
    return render(request, 'employee/employee_leave.html', context)


def add_employee(request):

    if request.method == "POST":

        form = add_employee_form(request.POST)

        if form.is_valid():
            employee = form.save(commit=False)
            temp_employee_id = (employee.last_name + "00000")
            user = User.objects.create_user(
                role='EMPLOYEE',
                username=temp_employee_id,
                password=employee.first_name + employee.last_name,)
            employee.account = user
            employee.save()
            employee.employee_id = (employee.last_name + f"{employee.id:05}")
            employee.save()
            user.username = employee.employee_id
            user.save()
            loan = loans.objects.create(
                employee = employee,

            )
            loan.save()
            return redirect('SIDEBUTTON-ADD-EMPLOYEE')

        else:
            print(form.errors)

    else:
        form = add_employee_form()

    return render(
        request,
        'sidebuttons/add_employee.html',
        {'form': form}
    )




def file_leave(request):
    from datetime import datetime
    from django.contrib import messages

    if request.method == "POST":

        leave_type = request.POST.get('leave_type')
        start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.POST.get("end_date"), "%Y-%m-%d").date()
        reason = request.POST.get('reason')
        emp_id = request.user

        employee = get_object_or_404(Employees, account=emp_id)

        leave = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

        LeaveHistory.objects.create(
            employee=employee,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            duration=leave.duration
        )

        messages.success(request, "Leave request submitted successfully!")
        return redirect('EMPLOYEE-LEAVE')

    return redirect('EMPLOYEE-LEAVE')


def DTR(request):
    from datetime import datetime
    emp_id = request.user.id
    employee = get_object_or_404(Employees, account=emp_id)
    
    # 1. Get Month and Year from Request (Default to current)
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # 2. Get number of days in that month
    num_days = calendar.monthrange(year, month)[1]
    
    # 3. Fetch all attendance logs for this employee in this month
    logs = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    )
    
    # Convert logs to a dictionary for easy lookup: {date: log_object}
    logs_dict = {log.date: log for log in logs}

    # 4. Prepare the Data for the Table
    dtr_data = []
    total_late_minutes = 0
    days_worked = 0

    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        log = logs_dict.get(current_date)
        
        day_info = {
            'day': day,
            'date': current_date,
            'is_weekend': current_date.weekday() >= 5, # 5=Sat, 6=Sun
            'in': None,
            'out': None,
            'late': 0,
        }

        if log:
            day_info['in'] = log.time_in
            day_info['out'] = log.time_out
            days_worked += 1
            
            # Simple Late Calculation (e.g., if later than 8:00 AM)
            if log.time_in:
                # Convert time_in to a naive time for comparison
                check_in = log.time_in.time()
                if check_in > datetime.strptime("07:00", "%H:%M").time():
                    # Calculate difference in minutes
                    diff = datetime.combine(date.today(), check_in) - datetime.combine(date.today(), datetime.strptime("07:00", "%H:%M").time())
                    day_info['late'] = diff.seconds // 60
                    total_late_minutes += day_info['late']

        dtr_data.append(day_info)
    
    context = {
        'employee': employee,
        'dtr_data': dtr_data,
        'days_worked': days_worked,
        'total_late': total_late_minutes,
        'selected_month': month,
        'selected_year': year,
    }
    
    return render(request, 'employee/employee_dtr.html', context)