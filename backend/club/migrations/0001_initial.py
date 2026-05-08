# Generated for the hardened current club app model state.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("initials", models.CharField(max_length=15)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("student_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("year_level", models.IntegerField(blank=True, choices=[(1, "1st Year"), (2, "2nd Year"), (3, "3rd Year"), (4, "4th Year"), (5, "5th Year")], null=True)),
                ("section", models.CharField(blank=True, max_length=20)),
                ("avatar", models.ImageField(blank=True, null=True, upload_to="avatars/")),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ActivityCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("color_code", models.CharField(default="#3B82F6", max_length=7)),
            ],
            options={"verbose_name_plural": "Activity Categories"},
        ),
        migrations.CreateModel(
            name="BudgetCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_income", models.BooleanField(default=False)),
            ],
            options={"verbose_name_plural": "Budget Categories"},
        ),
        migrations.CreateModel(
            name="DocumentCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
            ],
            options={"verbose_name_plural": "Document Categories"},
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="programs", to="club.department")),
            ],
        ),
        migrations.AddField(
            model_name="account",
            name="program",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="club.program"),
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("acronym", models.CharField(max_length=20)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="org_logos/")),
                ("description", models.TextField(blank=True)),
                ("mission", models.TextField(blank=True)),
                ("vision", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("active", "Active"), ("rejected", "Rejected"), ("suspended", "Suspended")], default="pending", max_length=20)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("status_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("leader", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="led_organization", to=settings.AUTH_USER_MODEL)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_organizations", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("officer", "Officer"), ("member", "Member")], default="member", max_length=20)),
                ("position", models.CharField(blank=True, max_length=100)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("role_changed_at", models.DateTimeField(blank=True, null=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="club.organization")),
                ("role_changed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="role_changes", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "organization")}},
        ),
        migrations.CreateModel(
            name="MembershipRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(blank=True, help_text="Why do you want to join?")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("rejection_reason", models.TextField(blank=True)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="membership_requests", to="club.organization")),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_requests", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="membership_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user", "organization")}},
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("venue", models.CharField(max_length=100)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("max_attendees", models.PositiveIntegerField(blank=True, null=True)),
                ("registration_deadline", models.DateTimeField(blank=True, null=True)),
                ("is_open_for_non_members", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="club.activitycategory")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="club.organization")),
            ],
            options={"ordering": ["-start_time"]},
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("time_in", models.DateTimeField(default=django.utils.timezone.now)),
                ("time_out", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("checked_in_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="attendance_checkins", to=settings.AUTH_USER_MODEL)),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="club.event")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("event", "user")}},
        ),
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("is_pinned", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="announcements", to=settings.AUTH_USER_MODEL)),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="announcements", to="club.organization")),
            ],
            options={"ordering": ["-is_pinned", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_type", models.CharField(choices=[("income", "Income"), ("expense", "Expense")], max_length=10)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("description", models.TextField()),
                ("date", models.DateField()),
                ("receipt", models.FileField(blank=True, null=True, upload_to="receipts/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="club.budgetcategory")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budget_entries", to=settings.AUTH_USER_MODEL)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budget_entries", to="club.organization")),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("file", models.FileField(upload_to="documents/")),
                ("visibility", models.CharField(choices=[("officers_only", "Officers Only"), ("members", "All Members"), ("public", "Public")], default="members", max_length=20)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="club.documentcategory")),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="club.organization")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="uploaded_documents", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
    ]
