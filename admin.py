from django.contrib import admin
from .models import UserAccount, LoginAttempt, SurveyResponse


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ("username", "password_type", "failed_count", "created_at")
    search_fields = ("username",)
    list_filter = ("password_type",)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("username", "password_type", "duration_ms", "success", "created_at")
    search_fields = ("username",)
    list_filter = ("password_type", "success")


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "used_password_type",
        "easier_to_remember",
        "faster_to_type",
        "real_life_choice",
    )
    search_fields = ("username",)