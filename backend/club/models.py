from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# --- Core Academic Models ---

class Department(models.Model):
    name = models.CharField(max_length=100)
    initials = models.CharField(max_length=15)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Program(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')

    def __str__(self):
        return self.name

# --- User Management ---

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class Account(AbstractBaseUser, PermissionsMixin):
    YEAR_LEVEL_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
        (5, '5th Year'),
    ]

    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True)
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES, null=True, blank=True)
    section = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# --- Organization Management ---

class Organization(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=100, unique=True)
    acronym = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='org_logos/', null=True, blank=True)
    description = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    
    # "One Student, One Org" Leader Rule
    leader = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='led_organization'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_organizations'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.filter(is_active=True).count()

    @property
    def officer_count(self):
        return self.members.filter(is_active=True, role='officer').count()

class Membership(models.Model):
    ROLE_CHOICES = [
        ('officer', 'Officer'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    position = models.CharField(max_length=100, blank=True)  # e.g., "President", "Secretary"
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    role_changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_changes'
    )
    role_changed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.email} - {self.organization.acronym} ({self.role})"

# --- Membership Request Management ---

class MembershipRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_requests')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='membership_requests')
    message = models.TextField(blank=True, help_text="Why do you want to join?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'organization')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} -> {self.organization.acronym} ({self.status})"

# --- Event Management ---

class ActivityCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#3B82F6')  # Hex color

    class Meta:
        verbose_name_plural = 'Activity Categories'

    def __str__(self):
        return self.name

class Event(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='events')
    category = models.ForeignKey(ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    venue = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    is_open_for_non_members = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.organization.acronym})"

    @property
    def attendee_count(self):
        return self.attendance_records.count()

    @property
    def is_full(self):
        if self.max_attendees:
            return self.attendee_count >= self.max_attendees
        return False

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_in = models.DateTimeField(default=timezone.now)
    time_out = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_checkins'
    )

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.email} @ {self.event.title}"

# --- Announcement Management ---

class Announcement(models.Model):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='announcements',
        null=True, 
        blank=True  # Null = system-wide announcement (admin only)
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    is_pinned = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        org_name = self.organization.acronym if self.organization else "SYSTEM"
        return f"[{org_name}] {self.title}"

# --- Budget Management ---

class BudgetCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_income = models.BooleanField(default=False)  # True for income categories, False for expense

    class Meta:
        verbose_name_plural = 'Budget Categories'

    def __str__(self):
        return f"{self.name} ({'Income' if self.is_income else 'Expense'})"

class Budget(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='budget_entries')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.ForeignKey(BudgetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.organization.acronym} - {self.transaction_type}: ₱{self.amount}"

# --- Document Management ---

class DocumentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Document Categories'

    def __str__(self):
        return self.name

class Document(models.Model):
    VISIBILITY_CHOICES = [
        ('officers_only', 'Officers Only'),
        ('members', 'All Members'),
        ('public', 'Public'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='documents')
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='members')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.organization.acronym} - {self.title}"

    @property
    def file_size(self):
        if self.file:
            return self.file.size
        return 0

    @property
    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ''
