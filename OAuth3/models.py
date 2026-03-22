import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


def default_mfa_expiration():
    return timezone.now() + timedelta(minutes=5)


class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    email = models.EmailField(max_length=120, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)

    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AppUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombres", "apellidos"]

    class Meta:
        db_table = "app_user"

    def __str__(self):
        return self.email


class MFAChallenge(models.Model):
    PURPOSE_CHOICES = [
        ("LOGIN", "LOGIN"),
        ("REGISTER", "REGISTER"),
        ("RESET_PASSWORD", "RESET_PASSWORD"),
        ("VERIFY_EMAIL", "VERIFY_EMAIL"),
    ]

    CHANNEL_CHOICES = [
        ("EMAIL", "EMAIL"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="mfa_challenges")
    code_hash = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="EMAIL")
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default="LOGIN")
    expires_at = models.DateTimeField(default=default_mfa_expiration)
    consumed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "mfa_challenge"

    def __str__(self):
        return f"{self.user.email} - {self.purpose}"
    
    