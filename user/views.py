from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """This method determines where to send the user after login"""
        user = self.request.user
        
        if user.role == "ADMIN":
            return reverse_lazy('admin-dashboard')
        elif user.role == "STAFF":
            return reverse_lazy('HR-DASHBOARD')
        elif user.role == "EMPLOYEE":
            return reverse_lazy('EMPLOYEE-DASHBOARD')
        else:
            # A fallback in case a user has no role
            return reverse_lazy('login')



@login_required
def Admin_dashboard(request):
    if request.user.role != "ADMIN":
        return redirect('login')
    return render(request, 'Admin_dashboard.html')