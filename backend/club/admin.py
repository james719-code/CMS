from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Account, ActivityCategory, Announcement, Attendance, Budget, BudgetCategory,
    Department, Document, DocumentCategory, Event, Membership, MembershipRequest,
    Organization, Program
)


@admin.register(Account)
class AccountAdmin(UserAdmin):
    model = Account
    list_display = ('email', 'student_id', 'first_name', 'last_name', 'program', 'year_level', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'program', 'year_level')
    search_fields = ('email', 'student_id', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('student_id', 'first_name', 'last_name', 'program', 'year_level', 'section', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'initials')
    search_fields = ('name', 'initials')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'leader', 'status', 'member_count', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('name', 'acronym', 'leader__email', 'leader__first_name', 'leader__last_name')
    readonly_fields = ('created_at', 'updated_at', 'member_count', 'officer_count')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'position', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'organization')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'organization__name', 'position')


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'status', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'organization', 'created_at', 'reviewed_at')
    search_fields = ('user__email', 'organization__name', 'message')


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code')
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'venue', 'start_time', 'end_time', 'attendee_count')
    list_filter = ('organization', 'category', 'is_open_for_non_members', 'start_time')
    search_fields = ('title', 'description', 'venue', 'organization__name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'time_in', 'time_out', 'checked_in_by')
    list_filter = ('event__organization', 'time_in')
    search_fields = ('event__title', 'user__email', 'user__first_name', 'user__last_name')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'author', 'is_pinned', 'is_published', 'created_at')
    list_filter = ('organization', 'is_pinned', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'author__email')


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_income')
    list_filter = ('is_income',)
    search_fields = ('name',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('organization', 'transaction_type', 'category', 'amount', 'date', 'created_by')
    list_filter = ('organization', 'transaction_type', 'category', 'date')
    search_fields = ('organization__name', 'description', 'created_by__email')


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'visibility', 'uploaded_by', 'uploaded_at')
    list_filter = ('organization', 'category', 'visibility', 'uploaded_at')
    search_fields = ('title', 'description', 'organization__name', 'uploaded_by__email')
