import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from employees.models import Employees
from .models import Attendance


def Scan_page(request):
    return render(request, 'scan.html')


def process_scan(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        uid  = data.get('rfid_uid')

        employee = Employees.objects.filter(RFID=uid).first()
        if not employee:
            return JsonResponse({"error": "Card not registered in system"}, status=404)

        today = timezone.localdate()
        now   = timezone.now()

        log, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
        )

        if created or not log.time_in:
            log.time_in = now
            action = "Time In"

            # Determine if the employee is late
            local_now = timezone.localtime(now)
            if local_now.time() > employee.duty_in:
                local_naive = local_now.replace(tzinfo=None)
                import datetime
                duty_dt     = datetime.datetime.combine(local_now.date(), employee.duty_in)
                mins_late   = int((local_naive - duty_dt).total_seconds() // 60)
                status_msg  = f"Good Morning, {employee.first_name}! You are {mins_late} minute(s) late."
            else:
                status_msg = f"Good Morning, {employee.first_name}! You are on time."

        elif not log.time_out:
            log.time_out = now
            action     = "Time Out"
            status_msg = f"Goodbye, {employee.first_name}! Take care."

        else:
            return JsonResponse({
                "name":  employee.first_name,
                "error": "You have already clocked out for today.",
            }, status=400)

        log.save()

        return JsonResponse({
            "name":       f"{employee.first_name} {employee.last_name}",
            "action":     action,
            "status_msg": status_msg,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
