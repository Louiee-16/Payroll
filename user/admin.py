from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['role']
    
    # This controls the EDIT user screen
    fieldsets = UserAdmin.fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )

    # THIS IS WHAT YOU NEED: This controls the ADD user screen (the one in your screenshot)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Management', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)