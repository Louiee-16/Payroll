import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from employees.models import Employees
from LEAVES.models import LeaveBalance
from LOGS.models import Attendance
from user.decorators import staff_required
from user.models import Notification, log_action


@staff_required
def HR_dashboard(request):
    import json
    import calendar as cal
    from django.db.models import Sum, Count
    from LEAVES.models import LeaveRequest

    today           = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)

    active_employees = Employees.objects.filter(is_archive=False)
    total_headcount  = active_employees.count()
    on_leave         = Employees.objects.filter(on_leave=True).count()
    recent_hires     = Employees.objects.filter(date_hired__gte=thirty_days_ago).count()
    contractuals     = active_employees.filter(status='CONTRACTUAL').count()
    permanents       = active_employees.filter(status='PERMANENT').count()

    # ── 1. Headcount by Department (pie chart) ──────────────────────────
    dept_qs = (
        active_employees
        .values('department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    dept_labels = [d['department'] for d in dept_qs]
    dept_data   = [d['count'] for d in dept_qs]

    # ── 2. Monthly Payroll Cost — last 6 months (bar chart) ─────────────
    payroll_labels = []
    payroll_data   = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
        month_name = cal.month_abbr[m]
        payroll_labels.append(f"{month_name} {y}")
        total = active_employees.aggregate(t=Sum('basic_pay'))['t'] or 0
        payroll_data.append(float(total))

    # ── 3. Attendance This Week (bar chart — present/absent/late) ───────
    week_start     = today - datetime.timedelta(days=today.weekday())
    att_labels     = []
    att_present    = []
    att_absent     = []
    att_late       = []
    for i in range(min(today.weekday() + 1, 5)):
        d = week_start + datetime.timedelta(days=i)
        att_labels.append(d.strftime('%a'))
        day_logs = Attendance.objects.filter(date=d).select_related('employee')
        present  = day_logs.filter(time_in__isnull=False).count()
        late     = sum(1 for log in day_logs if log.is_late)
        absent   = total_headcount - present
        att_present.append(present)
        att_absent.append(max(absent, 0))
        att_late.append(late)

    # ── 4. Leave Usage Breakdown (donut chart) ──────────────────────────
    leave_qs = (
        LeaveRequest.objects
        .filter(status='APPROVED')
        .values('leave_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    leave_type_map = dict(LeaveRequest.LEAVE_TYPES)
    leave_labels = [leave_type_map.get(l['leave_type'], l['leave_type']) for l in leave_qs]
    leave_data   = [l['count'] for l in leave_qs]

    # ── 5. Today's attendance quick stats ───────────────────────────────
    today_logs    = Attendance.objects.filter(date=today).select_related('employee')
    today_present = today_logs.filter(time_in__isnull=False).count()
    today_late    = sum(1 for log in today_logs if log.is_late)
    today_absent  = total_headcount - today_present

    context = {
        'total_headcount': total_headcount,
        'on_leave':        on_leave,
        'recent_hires':    recent_hires,
        'contractuals':    contractuals,
        'permanents':      permanents,
        'today_present':   today_present,
        'today_absent':    today_absent,
        'today_late':      today_late,
        # Chart data (JSON-safe)
        'dept_labels':     json.dumps(dept_labels),
        'dept_data':       json.dumps(dept_data),
        'payroll_labels':  json.dumps(payroll_labels),
        'payroll_data':    json.dumps(payroll_data),
        'att_labels':      json.dumps(att_labels),
        'att_present':     json.dumps(att_present),
        'att_absent':      json.dumps(att_absent),
        'att_late':        json.dumps(att_late),
        'leave_labels':    json.dumps(leave_labels),
        'leave_data':      json.dumps(leave_data),
    }
    return render(request, 'dashboards/HR_dashboard.html', context)


@staff_required
def ARCHIVE(request, id):
    employee = get_object_or_404(Employees, id=id)
    employee.is_archive = True
    employee.save()
    log_action(request, 'EMPLOYEE_ARCHIVED', f'Archived {employee.first_name} {employee.last_name} ({employee.employee_id}).')
    return JsonResponse({'success': True})


from django.contrib.auth.decorators import login_required

@login_required
def search_employees(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    from django.db.models import Q
    results = (
        Employees.objects
        .filter(is_archive=False)
        .filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(employee_id__icontains=q))
        [:8]
    )
    data = [
        {
            'id': e.id,
            'name': f"{e.first_name} {e.last_name}",
            'designation': e.designation,
            'department': e.department,
            'employee_id': e.employee_id,
        }
        for e in results
    ]
    return JsonResponse(data, safe=False)


@staff_required
def TEAM(request):
    thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

    employees    = Employees.objects.filter(is_archive=False)
    on_leave     = Employees.objects.filter(on_leave=True).count()
    recent_hires = Employees.objects.filter(date_hired__gte=thirty_days_ago).count()
    contractuals = Employees.objects.filter(status='CONTRACTUAL')
    scans        = Attendance.objects.all()

    context = {
        'employees':    employees,
        'on_leave':     on_leave,
        'recent_hires': recent_hires,
        'contractuals': contractuals,
        'scans':        scans,
    }
    return render(request, 'sidebuttons/teams.html', context)


@staff_required
def ONBOARD(request):
    return render(request, 'sidebuttons/onboard.html')


@staff_required
def LOGINS(request):
    today      = timezone.localdate()
    logs       = Attendance.objects.filter(date=today).select_related('employee')
    total_emps = Employees.objects.filter(is_archive=False).count()
    present    = logs.filter(time_in__isnull=False).count()
    absent     = total_emps - present
    late       = sum(1 for log in logs if log.is_late)

    context = {
        'today':           today,
        'total_employees': total_emps,
        'present_count':   present,
        'absent_count':    absent,
        'late_count':      late,
        'cutoff_time':     '7:00 AM',
        'logs':            logs,
    }
    return render(request, 'sidebuttons/logs.html', context)


@staff_required
def TIME_TRACKING(request):
    today      = timezone.localdate()
    attendance = Attendance.objects.filter(date=today).select_related('employee')
    total_emps = Employees.objects.filter(is_archive=False).count()
    active     = attendance.filter(time_in__isnull=False, time_out__isnull=True).count()
    late_count = sum(1 for a in attendance if a.is_late)
    rfid_count = Employees.objects.filter(is_archive=False).exclude(RFID__isnull=True).exclude(RFID='').count()
    missing    = total_emps - attendance.filter(time_in__isnull=False).count()

    context = {
        'attendance':  attendance,
        'active':      active,
        'late_count':  late_count,
        'scans':       attendance,
        'rfid_count':  rfid_count,
        'missing':     max(missing, 0),
    }
    return render(request, 'sidebuttons/time_tracking.html', context)


@staff_required
def ADD_EMPLOYEE(request):
    return render(request, 'sidebuttons/add_employee.html')


@staff_required
def employee_profile(request, emp_id):
    from payroll.views import (
        calculate_tax, calculate_pagibig, calculate_philhealth,
    )

    employee = get_object_or_404(Employees, id=emp_id)
    balance, _    = LeaveBalance.objects.get_or_create(employee=employee)
    loan_record   = employee.employee_loans.first()
    recent_logs   = Attendance.objects.filter(employee=employee).order_by('-date')[:10]

    # Payroll snapshot
    m = Decimal(str(employee.basic_pay))
    sss_ee     = (m * Decimal('0.05')).quantize(Decimal('0.01'))
    pagibig_ee = calculate_pagibig(m).quantize(Decimal('0.01'))
    phil_ee    = calculate_philhealth(m).quantize(Decimal('0.01'))
    bonus_excess = max(m - Decimal('90000'), Decimal('0')) / Decimal('12')
    taxable = m + bonus_excess - sss_ee - pagibig_ee - phil_ee
    tax = calculate_tax(taxable).quantize(Decimal('0.01'))
    loan_monthly = Decimal(str(loan_record.monthly_deductions)) if loan_record else Decimal('0')
    total_ded = (tax + sss_ee + pagibig_ee + phil_ee + Decimal('300') + loan_monthly).quantize(Decimal('0.01'))
    net_pay = (m - total_ded).quantize(Decimal('0.01'))

    context = {
        'emp':          employee,
        'balance':      balance,
        'loan_record':  loan_record,
        'loan_monthly': loan_monthly,
        'recent_logs':  recent_logs,
        'salary':       m,
        'sss':          sss_ee,
        'pagibig':      pagibig_ee,
        'philhealth':   phil_ee,
        'tax':          tax,
        'total_ded':    total_ded,
        'net_pay':      net_pay,
    }
    return render(request, 'sidebuttons/employee_profile.html', context)


@staff_required
def edit_employee(request, emp_id):
    from django.contrib import messages
    from employees.forms import EditEmployeeForm

    employee = get_object_or_404(Employees, id=emp_id)

    if request.method == 'POST':
        form = EditEmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            log_action(request, 'EMPLOYEE_EDITED', f'Edited {employee.first_name} {employee.last_name} ({employee.employee_id}).')
            messages.success(request, f"{employee.first_name} {employee.last_name}'s record has been updated.")
            return redirect('EMPLOYEE-PROFILE', emp_id=emp_id)
    else:
        form = EditEmployeeForm(instance=employee)

    return render(request, 'sidebuttons/edit_employee.html', {'form': form, 'emp': employee})


@staff_required
def reset_employee_password(request, emp_id):
    from django.contrib import messages

    employee = get_object_or_404(Employees, id=emp_id)
    user = employee.account

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password and len(new_password) >= 6:
            user.set_password(new_password)
            user.save()

            Notification.objects.create(
                recipient=user,
                notification_type='PASSWORD_RESET',
                message='Your password has been reset by HR. Please log in with your new password.',
            )
            log_action(request, 'PASSWORD_RESET', f'Reset password for {employee.first_name} {employee.last_name} ({employee.employee_id}).')

            messages.success(request, f"Password for {employee.first_name} {employee.last_name} has been reset.")
        else:
            messages.error(request, "Password must be at least 6 characters.")

    return redirect('EMPLOYEE-PROFILE', emp_id=emp_id)
