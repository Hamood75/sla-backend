from django.contrib import admin

from .models import EmployeeProfile, ProfileProject, ProfileSocialLink


class ProfileSocialLinkInline(admin.TabularInline):
    model = ProfileSocialLink
    extra = 1


class ProfileProjectInline(admin.TabularInline):
    model = ProfileProject
    extra = 1


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'username', 'position', 'is_public', 'department']
    list_filter = ['is_public', 'department']
    search_fields = ['display_name', 'username', 'email']
    prepopulated_fields = {'username': ('display_name',)}
    inlines = [ProfileSocialLinkInline, ProfileProjectInline]
