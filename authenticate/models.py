from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class University(models.Model):
    name = models.CharField(max_length=100, unique=True)
    directorate = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Universities"
        ordering = ['name']

class College(models.Model):
    name = models.CharField(max_length=100, unique=True)
    directorate = models.CharField(max_length=255)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    nss_unit = models.IntegerField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.university.name})"

    class Meta:
        ordering = ['university__name', 'name']

class User(AbstractUser):
    USER_TYPE_CHOICES = (
    ('university', 'University'),
    ('college', 'College'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True, blank=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)

    # Add these to resolve the reverse accessor clashes
    groups = models.ManyToManyField(
    'auth.Group',
    verbose_name='groups',
    blank=True,
    help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    related_name="custom_user_set",  # Changed from 'user_set'
    related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
    'auth.Permission',
    verbose_name='user permissions',
    blank=True,
    help_text='Specific permissions for this user.',
    related_name="custom_user_set",  # Changed from 'user_set'
    related_query_name="user",
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"