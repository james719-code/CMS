from django.db import models
from django.utils import timezone  # Import timezone to handle time zones

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    initials = models.CharField(max_length=15)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Program(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    initials = models.CharField(max_length=15)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('admin', 'Admin'),
        ('officer', 'Officer'),
        ('member', 'Member'),
    ]
    id = models.AutoField(primary_key=True)
    account = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)

    def __str__(self):
        return self.account


class Class(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)
    section = models.CharField(max_length=10)
    year = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.section}"


class Officer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='officer_profile', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='officers', null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='officers', null=True, blank=True)
    position = models.CharField(max_length=100)
    class_include = models.OneToOneField(Class, on_delete=models.SET_NULL, blank=True, null=True, related_name='officer')

    def __str__(self):
        return self.user.account if self.user else "Unassigned Officer"


class Member(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='member_profile', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='members', null=True, blank=True)

    def __str__(self):
        return self.user.account if self.user else "Unassigned Member"


class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='admin_profile', null=True, blank=True)
    work = models.CharField(max_length=100)

    def __str__(self):
        return self.user.account if self.user else "Unassigned Admin"


class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='organizations', null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='organizations', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
