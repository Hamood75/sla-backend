from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Department, Organization, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ['username', 'email', 'role', 'job_title', 'department', 'is_staff']
    list_filter = ['role', 'is_staff', 'department']
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Street Labs', {'fields': ('role', 'phone', 'department', 'job_title', 'photo', 'is_staff_member')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Street Labs', {'fields': ('role', 'phone', 'department', 'job_title')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_partner', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
