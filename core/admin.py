from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Application, Candidate, Employer, Job, User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "phone", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


class EmployerInline(admin.StackedInline):
    model = Employer
    can_delete = False
    max_num = 1


class CandidateInline(admin.StackedInline):
    model = Candidate
    can_delete = False
    max_num = 1


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    ordering = ("-created_at",)
    list_display = ("email", "role", "phone", "is_active", "is_verified", "created_at")
    list_filter = ("role", "is_active", "is_verified", "is_staff")
    search_fields = ("email", "phone")
    readonly_fields = ("created_at", "updated_at", "last_login")
    actions = ["mark_verified", "deactivate_users"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        ("Role and status", {"fields": ("role", "is_active", "is_verified")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "role", "password1", "password2"),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.role == User.Role.EMPLOYER:
            return [EmployerInline]
        if obj.role == User.Role.CANDIDATE:
            return [CandidateInline]
        return []

    @admin.action(description="Mark selected users as verified")
    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)


admin.site.register(Employer)
admin.site.register(Candidate)
admin.site.register(Job)
admin.site.register(Application)