from django.shortcuts import render, redirect, get_object_or_404
from .models import LeaveRequest, LeaveHistory
from django.contrib import messages

def SIDEBUTTON_LEAVE(request):
    leaves = LeaveRequest.objects.all().order_by('-requested_at')
    
    stats = {
        'pending': LeaveRequest.objects.filter(status='PENDING').count(),
        'approved': LeaveRequest.objects.filter(status='APPROVED').count(),
        'total': leaves.count()
    }
    
    return render(request, 'sidebuttons/leave.html', {'leaves': leaves, 'stats': stats})

def update_leave_status(request, leave_id, status):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave_history = LeaveHistory.objects.all().order_by('-requested_at').first()
    if status in ['APPROVED', 'REJECTED']:
        leave_history.status = status
        leave.status = status
        leave_history.save()
        leave.save()
     
        messages.success(request, f"Leave request for {leave.employee.first_name} has been {status.lower()}.")
    return redirect('SIDEBUTTON-LEAVE')

