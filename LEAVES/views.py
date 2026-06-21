from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from employees.models import Employees
from user.decorators import staff_required
from user.models import Notification, User, log_action

from .models import LeaveBalance, LeaveHistory, LeaveRequest

CREDIT_LEAVE_TYPES = [
    ('solo_parent',  'Solo Parent Leave',  7),
    ('maternity',    'Maternity Leave',    105),
    ('paternity',    'Paternity Leave',    7),
]


@staff_required
def SIDEBUTTON_LEAVE(request):
    leaves    = LeaveRequest.objects.all().order_by('-requested_at')
    employees = Employees.objects.all()
    stats = {
        'pending':  LeaveRequest.objects.filter(status='PENDING').count(),
        'approved': LeaveRequest.objects.filter(status='APPROVED').count(),
        'total':    leaves.count(),
    }
    context = {
        'leaves':             leaves,
        'stats':              stats,
        'employees':          employees,
        'credit_leave_types': CREDIT_LEAVE_TYPES,
    }
    return render(request, 'sidebuttons/leave.html', context)


@staff_required
def credit_leave(request):
    if request.method == 'POST':
        emp_id     = request.POST.get('employee_id')
        leave_field = request.POST.get('leave_field')
        days       = request.POST.get('days')

        employee = get_object_or_404(Employees, id=emp_id)
        balance, _ = LeaveBalance.objects.get_or_create(employee=employee)

        valid_fields = {t[0] for t in CREDIT_LEAVE_TYPES}
        if leave_field in valid_fields and days:
            current = getattr(balance, leave_field)
            setattr(balance, leave_field, current + Decimal(days))
            balance.save()

            label = dict((t[0], t[1]) for t in CREDIT_LEAVE_TYPES).get(leave_field, leave_field)

            Notification.objects.create(
                recipient=employee.account,
                notification_type='LEAVE_CREDITED',
                message=f"HR credited {days} day(s) of {label} to your leave balance.",
                link='/employee/leave',
            )

            log_action(request, 'LEAVE_CREDITED', f'Credited {days}d of {label} to {employee.first_name} {employee.last_name}.')
            messages.success(
                request,
                f"Credited {days} day(s) of {label} to {employee.first_name} {employee.last_name}."
            )

    return redirect('SIDEBUTTON-LEAVE')


@staff_required
def update_leave_status(request, leave_id, status):
    leave = get_object_or_404(LeaveRequest, id=leave_id)

    if status in ['APPROVED', 'REJECTED']:
        leave.status = status
        leave.save()

        # Deduct from balance only when approving
        if status == 'APPROVED':
            balance, _ = LeaveBalance.objects.get_or_create(employee=leave.employee)
            balance.deduct(leave.leave_type, leave.duration)

        LeaveHistory.objects.filter(
            employee=leave.employee,
            start_date=leave.start_date,
            end_date=leave.end_date,
            status='PENDING',
        ).update(status=status)

        Notification.objects.create(
            recipient=leave.employee.account,
            notification_type='LEAVE_APPROVED' if status == 'APPROVED' else 'LEAVE_REJECTED',
            message=f"Your {leave.get_leave_type_display()} ({leave.duration} day(s)) has been {status.lower()}.",
            link='/employee/leave',
        )

        action = 'LEAVE_APPROVED' if status == 'APPROVED' else 'LEAVE_REJECTED'
        log_action(request, action, f'{status.title()} {leave.get_leave_type_display()} for {leave.employee.first_name} {leave.employee.last_name} ({leave.duration}d).')

        messages.success(
            request,
            f"Leave request for {leave.employee.first_name} has been {status.lower()}."
        )
    return redirect('SIDEBUTTON-LEAVE')
