from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from accounts.managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique primary login identifier.
    Inherits from AbstractBaseUser and PermissionsMixin.
    """

    email = models.EmailField(
        unique=True,
        max_length=255,
        db_index=True,
        help_text='Unique email address used for login and notifications.'
    )
    name = models.CharField(
        max_length=255,
        help_text='Full name of the user.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user account should be treated as active.'
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.'
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the user account was registered.'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email
