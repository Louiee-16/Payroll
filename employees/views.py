import calendar
import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from LEAVES.models import LeaveBalance, LeaveHistory, LeaveRequest
from LOANS.models import loans
from LOGS.models import Attendance
from user.decorators import employee_required, staff_required
from user.models import Notification, User, log_action

from .forms import add_employee_form
from .models import Employees


@employee_required
def employee_dashboard(request):
    from payroll.views import calculate_tax, calculate_pagibig, calculate_philhealth

    employee = get_object_or_404(Employees, account=request.user)
    balance, _ = LeaveBalance.objects.get_or_create(employee=employee)

    recent_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-requested_at')[:5]

    loan_record = employee.employee_loans.first()
    loan_total   = float(loan_record.total_loans) if loan_record else 0
    loan_monthly = float(loan_record.monthly_deductions) if loan_record else 0

    m = Decimal(str(employee.basic_pay))
    sss_ee     = (m * Decimal('0.05')).quantize(Decimal('0.01'))
    pagibig_ee = calculate_pagibig(m).quantize(Decimal('0.01'))
    phil_ee    = calculate_philhealth(m).quantize(Decimal('0.01'))
    bonus_excess = max(m - Decimal('90000'), Decimal('0')) / Decimal('12')
    taxable = m + bonus_excess - sss_ee - pagibig_ee - phil_ee
    tax = calculate_tax(taxable).quantize(Decimal('0.01'))
    total_ded = (tax + sss_ee + pagibig_ee + phil_ee + Decimal('300') + Decimal(str(loan_monthly))).quantize(Decimal('0.01'))
    net_pay = (m - total_ded).quantize(Decimal('0.01'))

    context = {
        'employee':      employee,
        'balance':       balance,
        'recent_leaves': recent_leaves,
        'loan_total':    loan_total,
        'loan_monthly':  loan_monthly,
        'net_pay':       net_pay,
        'salary':        m,
    }
    return render(request, 'employee/employee_dashboard.html', context)


@employee_required
def employee_leave(request):
    employee = get_object_or_404(Employees, account=request.user)
    balance, _ = LeaveBalance.objects.get_or_create(employee=employee)
    history = LeaveHistory.objects.filter(employee=employee).order_by('-requested_at')

    context = {
        'employee': employee,
        'balance':  balance,
        'history':  history,
        'today':    datetime.date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'employee/employee_leave.html', context)


@staff_required
def add_employee(request):
    if request.method == "POST":
        form = add_employee_form(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            temp_employee_id = employee.last_name + "00000"
            user = User.objects.create_user(
                role='EMPLOYEE',
                username=temp_employee_id,
                password=employee.first_name + employee.last_name,
            )
            employee.account = user
            employee.save()
            employee.employee_id = employee.last_name + f"{employee.id:05}"
            employee.save()
            user.username = employee.employee_id
            user.save()
            loans.objects.create(employee=employee)
            LeaveBalance.objects.create(employee=employee)
            log_action(request, 'EMPLOYEE_CREATED', f'Created employee {employee.first_name} {employee.last_name} ({employee.employee_id}).')
            return redirect('SIDEBUTTON-ADD-EMPLOYEE')
    else:
        form = add_employee_form()

    return render(request, 'sidebuttons/add_employee.html', {'form': form})


@employee_required
def file_leave(request):
    if request.method == "POST":
        leave_type = request.POST.get('leave_type')
        start_date = datetime.datetime.strptime(request.POST.get("start_date"), "%Y-%m-%d").date()
        end_date   = datetime.datetime.strptime(request.POST.get("end_date"),   "%Y-%m-%d").date()
        reason     = request.POST.get('reason')
        duration   = (end_date - start_date).days + 1

        employee = get_object_or_404(Employees, account=request.user)
        balance, _ = LeaveBalance.objects.get_or_create(employee=employee)

        remaining = balance.get_balance(leave_type)
        if remaining < duration:
            messages.error(
                request,
                f"Insufficient {dict(LeaveRequest.LEAVE_TYPES).get(leave_type, leave_type)} balance. "
                f"You have {remaining} day(s) but requested {duration}."
            )
            return redirect('EMPLOYEE-LEAVE')

        leave = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        LeaveHistory.objects.create(
            employee=employee,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            duration=leave.duration,
        )

        # Notify all HR staff
        leave_label = dict(LeaveRequest.LEAVE_TYPES).get(leave_type, leave_type)
        for hr_user in User.objects.filter(role='STAFF'):
            Notification.objects.create(
                recipient=hr_user,
                notification_type='LEAVE_FILED',
                message=f"{employee.first_name} {employee.last_name} filed {leave_label} for {duration} day(s).",
                link='/leaves/admin/',
            )

        log_action(request, 'LEAVE_FILED', f'Filed {leave_label} for {duration} day(s).')
        messages.success(request, "Leave request submitted successfully!")

    return redirect('EMPLOYEE-LEAVE')


@employee_required
def DTR(request):
    employee = get_object_or_404(Employees, account=request.user)

    today = datetime.date.today()
    month = int(request.GET.get('month', today.month))
    year  = int(request.GET.get('year',  today.year))

    num_days = calendar.monthrange(year, month)[1]

    logs_qs   = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
    )
    logs_dict = {log.date: log for log in logs_qs}

    dtr_data           = []
    total_late_minutes = 0
    days_worked        = 0

    for day in range(1, num_days + 1):
        current_date = datetime.date(year, month, day)
        log = logs_dict.get(current_date)

        day_info = {
            'day':        day,
            'date':       current_date,
            'is_weekend': current_date.weekday() >= 5,
            'in':         None,
            'out':        None,
            'late':       0,
        }

        if log:
            day_info['in']  = log.time_in
            day_info['out'] = log.time_out
            days_worked += 1

            if log.time_in:
                from django.utils import timezone as tz
                local_in = tz.localtime(log.time_in).time()
                if local_in > employee.duty_in:
                    diff = (
                        datetime.datetime.combine(today, local_in)
                        - datetime.datetime.combine(today, employee.duty_in)
                    )
                    day_info['late']    = diff.seconds // 60
                    total_late_minutes += day_info['late']

        dtr_data.append(day_info)

    context = {
        'employee':       employee,
        'dtr_data':       dtr_data,
        'days_worked':    days_worked,
        'total_late':     total_late_minutes,
        'selected_month': month,
        'selected_year':  year,
    }

    return render(request, 'employee/employee_DTR.html', context)


@employee_required
def employee_payslip(request):
    from payroll.views import calculate_tax, calculate_sss, calculate_pagibig, calculate_philhealth
    import calendar as cal

    employee = get_object_or_404(Employees, account=request.user)
    m = Decimal(str(employee.basic_pay))

    today        = datetime.date.today()
    last_day     = cal.monthrange(today.year, today.month)[1]
    period_start = today.replace(day=1)
    period_end   = today.replace(day=last_day)
    period_str   = f"{period_start.strftime('%b %d, %Y')} - {period_end.strftime('%b %d, %Y')}"

    sss_ee     = (m * Decimal('0.05')).quantize(Decimal('0.01'))
    pagibig_ee = calculate_pagibig(m).quantize(Decimal('0.01'))
    phil_ee    = calculate_philhealth(m).quantize(Decimal('0.01'))
    coop_share = Decimal('300')

    bonus_excess = max(m - Decimal('90000'), Decimal('0')) / Decimal('12')
    taxable = m + bonus_excess - sss_ee - pagibig_ee - phil_ee
    tax = calculate_tax(taxable).quantize(Decimal('0.01'))

    loan_record = employee.employee_loans.first()

    def lv(field):
        if loan_record:
            v = getattr(loan_record, field, None)
            return Decimal(str(v)) if v else Decimal('0')
        return Decimal('0')

    loan_items = [
        ('SSS Salary Loan',   lv('SSS_salary_monthly')),
        ('SSS Calamity',      lv('SSS_calamity_monthly')),
        ('SSS MPL',           lv('SSS_MPL_monthly')),
        ('SSS Educational',   lv('SSS_educ_monthly')),
        ('Pag-IBIG Housing',  lv('PAGIBIG_housing_monthly')),
        ('Pag-IBIG MPL',      lv('PAGIBIG_MPL_monthly')),
        ('Coop Loan',         lv('COOP_monthly')),
    ]
    active_loans = [(name, amt) for name, amt in loan_items if amt > 0]
    total_loans  = sum(amt for _, amt in active_loans)

    from payroll.views import calculate_overtime, calculate_13th_month

    # OT for current month
    current_month_logs = Attendance.objects.filter(
        employee=employee,
        date__year=today.year, date__month=today.month,
    )
    ot_hours, ot_pay = calculate_overtime(list(current_month_logs), employee.duty_out, m)

    # 13th month accrual
    thirteenth_month = calculate_13th_month(m, employee.date_hired)

    total_deductions = (tax + sss_ee + pagibig_ee + phil_ee + coop_share + total_loans).quantize(Decimal('0.01'))
    gross_with_ot = (m + ot_pay).quantize(Decimal('0.01'))
    net_pay = (gross_with_ot - total_deductions).quantize(Decimal('0.01'))

    balance, _ = LeaveBalance.objects.get_or_create(employee=employee)

    from payroll.models import PayrollPeriod
    past_payslips = PayrollPeriod.objects.filter(employee=employee).order_by('-start_date')[:12]

    context = {
        'employee':     employee,
        'period_str':   period_str,
        'gross_with_ot': gross_with_ot,
        'salary':       m,
        'tax':          tax,
        'sss':          sss_ee,
        'pagibig':      pagibig_ee,
        'philhealth':   phil_ee,
        'coop_share':   coop_share,
        'active_loans': active_loans,
        'total_loans':  total_loans,
        'total_deductions': total_deductions,
        'net_pay':      net_pay,
        'first_half':   (net_pay / 2).quantize(Decimal('0.01')),
        'second_half':  (net_pay / 2).quantize(Decimal('0.01')),
        'balance':          balance,
        'past_payslips':    past_payslips,
        'ot_hours':         ot_hours,
        'ot_pay':           ot_pay,
        'thirteenth_month': thirteenth_month,
    }
    return render(request, 'employee/employee_payslip.html', context)


@login_required
def change_password(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_action(request, 'PASSWORD_CHANGED', f'{request.user.username} changed their password.')
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('EMPLOYEE-DASHBOARD')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'employee/change_password.html', {'form': form})
