from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from simple_history.models import HistoricalRecords

from django.utils.translation import gettext_lazy as _
from accounts.models.agency import Agency


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where username is the unique identifier for authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The username must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    history = HistoricalRecords()

    username = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=True,
        null=True
    )
    full_name = models.CharField(
        max_length=255
    )
    contact_no = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agencyuser', 'Agency User'),
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )
    is_default_user = models.BooleanField(
        default=False
    )
    is_blocked = models.BooleanField(
        default=False
    )
    agency = models.ForeignKey(
        Agency,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='users'
    )

    # Essential fields for admin and authentication
    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField(
        default=False
    )

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Add additional required fields if needed

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username or self.full_name
