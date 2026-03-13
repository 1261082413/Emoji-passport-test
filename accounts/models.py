from django.db import models
from django.utils import timezone


class UserAccount(models.Model):
    PASSWORD_CHOICES = [
        ("text", "Text"),
        ("emoji", "Emoji"),
        ("mix", "Mix"),
    ]

    username = models.CharField(max_length=50)
    password_hash = models.CharField(max_length=128)
    password_type = models.CharField(max_length=10, choices=PASSWORD_CHOICES)
    failed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("username", "password_type")

    def __str__(self):
        return f"{self.username} - {self.password_type}"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=50)
    password_type = models.CharField(max_length=10, choices=UserAccount.PASSWORD_CHOICES)
    duration_ms = models.IntegerField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} {self.password_type} {self.success} {self.duration_ms}ms"


class SurveyResponse(models.Model):
    username = models.CharField(max_length=50, unique=True)
    used_password_type = models.CharField(max_length=20)
    easier_to_remember = models.CharField(max_length=20)
    faster_to_type = models.CharField(max_length=20)
    real_life_choice = models.CharField(max_length=20)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Survey - {self.username}"