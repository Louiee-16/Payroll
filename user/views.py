from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .models import Notification

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS    = 900  # 15 minutes


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def _cache_key(self, username):
        return f'login_attempts_{username}'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        key      = self._cache_key(username)
        attempts = cache.get(key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            messages.error(request, 'Account temporarily locked. Try again in 15 minutes.')
            return render(request, self.template_name, {'form': self.get_form()})

        response = super().post(request, *args, **kwargs)

        if not request.user.is_authenticated:
            cache.set(key, attempts + 1, LOCKOUT_SECONDS)
            remaining = MAX_LOGIN_ATTEMPTS - attempts - 1
            if remaining > 0:
                messages.error(request, f'Invalid credentials. {remaining} attempt(s) remaining.')
            else:
                messages.error(request, 'Account temporarily locked. Try again in 15 minutes.')
        else:
            cache.delete(key)
            from .models import log_action
            log_action(request, 'LOGIN', f'{request.user.username} logged in.')

        return response

    def get_success_url(self):
        user = self.request.user
        if user.role == "ADMIN":
            return reverse_lazy('admin-dashboard')
        elif user.role == "STAFF":
            return reverse_lazy('HR-DASHBOARD')
        elif user.role == "EMPLOYEE":
            return reverse_lazy('EMPLOYEE-DASHBOARD')
        else:
            return reverse_lazy('login')



@login_required
def Admin_dashboard(request):
    if request.user.role != "ADMIN":
        return redirect('login')
    return render(request, 'Admin_dashboard.html')


@login_required
def notifications_page(request):
    notifications = request.user.notifications.all()[:50]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True})


@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


from user.decorators import staff_required as _staff_required

@_staff_required
def audit_log_page(request):
    from .models import AuditLog
    logs = AuditLog.objects.select_related('user').all()[:100]
    return render(request, 'audit_log.html', {'logs': logs})