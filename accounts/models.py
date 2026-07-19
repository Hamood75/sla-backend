from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ADMIN = 'admin', 'Admin'
        EDITOR = 'editor', 'Editor'
        EMPLOYEE = 'employee', 'Employee'
        PARTNER = 'partner', 'Partner'

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField(max_length=32, blank=True)
    department = models.ForeignKey(
        'accounts.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='members',
    )
    job_title = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)
    is_staff_member = models.BooleanField(default=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_backoffice_user(self):
        return self.is_superuser or self.role in {
            self.Role.SUPER_ADMIN,
            self.Role.ADMIN,
            self.Role.EDITOR,
        }


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='organizations/', blank=True, null=True)
    is_partner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
