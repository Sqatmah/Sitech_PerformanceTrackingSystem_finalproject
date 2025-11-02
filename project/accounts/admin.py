from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, ManagerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'profile_picture', 'phone_number', 'date_of_birth', 'bio')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'profile_picture', 'phone_number', 'date_of_birth', 'bio')
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'manager', 'enrollment_date', 'is_active')
    list_filter = ('is_active', 'enrollment_date', 'manager')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'student_id')
    raw_id_fields = ('user', 'manager')


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'hire_date', 'student_count')
    list_filter = ('department', 'hire_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
    raw_id_fields = ('user',)
