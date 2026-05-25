from django.urls import path
from . import views

urlpatterns = [
    path('leaves/admin/', views.SIDEBUTTON_LEAVE, name='SIDEBUTTON-LEAVE'),
    path('leaves/update/<int:leave_id>/<str:status>/', views.update_leave_status, name='UPDATE-LEAVE'),
]