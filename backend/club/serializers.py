from rest_framework import serializers
from django.utils import timezone
from .models import (
    Account, Department, Program, Organization,
    Membership, MembershipRequest, Event, Attendance,
    Announcement, Budget, BudgetCategory, Document, DocumentCategory,
    ActivityCategory, EventRegistration, Fee, FeeAssignment, Payment,
    Notification
)
from .validators import validate_document_file, validate_image_file, validate_receipt_file

# --- Core Academic Serializers ---

class DepartmentSerializer(serializers.ModelSerializer):
    program_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'initials', 'description', 'program_count']

    def get_program_count(self, obj):
        return obj.programs.count()

class ProgramSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'description', 'department', 'department_details']

# --- Account Serializers ---

class AccountSerializer(serializers.ModelSerializer):
    program_details = ProgramSerializer(source='program', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'email', 'student_id', 'first_name', 'last_name', 'full_name',
            'program', 'program_details', 'year_level', 'section', 'avatar', 
            'is_staff', 'is_active', 'date_joined', 'password'
        ]
        read_only_fields = ['is_staff', 'is_active', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True}
        }

    def validate_avatar(self, value):
        return validate_image_file(value)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Password is required.'})
        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class SimpleAccountSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Account
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'student_id', 'avatar', 'year_level', 'section']

# --- Organization Serializers ---

class OrganizationSerializer(serializers.ModelSerializer):
    leader_details = SimpleAccountSerializer(source='leader', read_only=True)
    member_count = serializers.ReadOnlyField()
    officer_count = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'acronym', 'logo', 'description', 'mission', 'vision',
            'leader', 'leader_details', 'status', 'created_at', 'updated_at',
            'member_count', 'officer_count', 'reviewed_by', 'reviewed_at', 'status_note'
        ]
        read_only_fields = [
            'status', 'created_at', 'updated_at', 'leader',
            'reviewed_by', 'reviewed_at', 'status_note'
        ]

    def validate_logo(self, value):
        return validate_image_file(value)

class OrganizationRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'acronym', 'description', 'mission', 'vision', 'logo']

    def validate_logo(self, value):
        return validate_image_file(value)

    def validate(self, data):
        user = self.context['request'].user
        if Organization.objects.filter(leader=user).exists():
            raise serializers.ValidationError(
                "You are already leading an organization. One student can only lead one organization."
            )
        return data

class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    leader_name = serializers.CharField(source='leader.full_name', read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'acronym', 'logo', 'status', 'leader_name', 'member_count', 'created_at']

# --- Membership Serializers ---

class MembershipSerializer(serializers.ModelSerializer):
    user_details = SimpleAccountSerializer(source='user', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_acronym = serializers.CharField(source='organization.acronym', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_details', 'organization', 'organization_name',
            'organization_acronym', 'role', 'position', 'date_joined', 'updated_at',
            'is_active', 'role_changed_by', 'role_changed_at'
        ]
        read_only_fields = [
            'role', 'position', 'date_joined', 'updated_at', 'is_active',
            'role_changed_by', 'role_changed_at'
        ]

class MembershipRequestSerializer(serializers.ModelSerializer):
    user_details = SimpleAccountSerializer(source='user', read_only=True)
    organization_details = OrganizationListSerializer(source='organization', read_only=True)
    reviewed_by_details = SimpleAccountSerializer(source='reviewed_by', read_only=True)

    class Meta:
        model = MembershipRequest
        fields = [
            'id', 'user', 'user_details', 'organization', 'organization_details',
            'message', 'status', 'created_at', 'reviewed_by', 'reviewed_by_details',
            'reviewed_at', 'rejection_reason'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'reviewed_by', 'reviewed_at']

    def validate(self, data):
        user = self.context['request'].user
        organization = data.get('organization')
        if organization and organization.status != 'active':
            raise serializers.ValidationError("You can only request membership in active organizations.")
        
        # Check if already a member
        if Membership.objects.filter(user=user, organization=organization).exists():
            raise serializers.ValidationError("You are already a member of this organization.")
        
        # Check if already has a pending request
        if MembershipRequest.objects.filter(user=user, organization=organization, status='pending').exists():
            raise serializers.ValidationError("You already have a pending request for this organization.")
        
        return data

# --- Event & Attendance Serializers ---

class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ['id', 'name', 'description', 'color_code']

class EventSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_acronym = serializers.CharField(source='organization.acronym', read_only=True)
    category_details = ActivityCategorySerializer(source='category', read_only=True)
    attendee_count = serializers.ReadOnlyField()
    registration_count = serializers.ReadOnlyField()
    waitlist_count = serializers.ReadOnlyField()
    is_registration_full = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'organization', 'organization_name', 'organization_acronym',
            'category', 'category_details', 'title', 'description', 'venue',
            'start_time', 'end_time', 'max_attendees', 'registration_deadline',
            'is_open_for_non_members', 'attendee_count', 'registration_count',
            'waitlist_count', 'is_registration_full', 'is_full',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = data.get('end_time', getattr(self.instance, 'end_time', None))
        registration_deadline = data.get(
            'registration_deadline',
            getattr(self.instance, 'registration_deadline', None)
        )
        max_attendees = data.get('max_attendees', getattr(self.instance, 'max_attendees', None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("Event end time must be after start time.")
        if registration_deadline and start_time and registration_deadline > start_time:
            raise serializers.ValidationError("Registration deadline must be before the event starts.")
        if max_attendees is not None and max_attendees < 1:
            raise serializers.ValidationError("Maximum attendees must be at least 1.")
        return data

class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    organization_acronym = serializers.CharField(source='organization.acronym', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    attendee_count = serializers.ReadOnlyField()
    registration_count = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'venue', 'start_time', 'end_time',
            'organization_acronym', 'category_name', 'attendee_count',
            'registration_count', 'is_open_for_non_members'
        ]

class EventRegistrationSerializer(serializers.ModelSerializer):
    user_details = SimpleAccountSerializer(source='user', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    organization = serializers.IntegerField(source='event.organization_id', read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            'id', 'event', 'event_title', 'organization', 'user', 'user_details',
            'status', 'notes', 'registered_at', 'updated_at', 'cancelled_at'
        ]
        read_only_fields = ['status', 'registered_at', 'updated_at', 'cancelled_at']
        extra_kwargs = {
            'user': {'required': False}
        }

    def validate(self, data):
        request = self.context['request']
        event = data.get('event', getattr(self.instance, 'event', None))
        registration_user = data.get('user', request.user)

        if event and event.end_time < timezone.now():
            raise serializers.ValidationError("Registration is closed for past events.")
        if event and event.registration_deadline and event.registration_deadline < timezone.now():
            raise serializers.ValidationError("Registration deadline has passed.")
        if event and not event.is_open_for_non_members and not Membership.objects.filter(
            user=registration_user,
            organization=event.organization,
            is_active=True,
        ).exists() and event.organization.leader != registration_user:
            raise serializers.ValidationError("Only members can register for this event.")

        return data

class AttendanceSerializer(serializers.ModelSerializer):
    user_details = SimpleAccountSerializer(source='user', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'event', 'event_title', 'user', 'user_details',
            'time_in', 'time_out', 'notes', 'checked_in_by'
        ]
        read_only_fields = ['checked_in_by']

# --- Dues & Payment Serializers ---

class FeeSerializer(serializers.ModelSerializer):
    created_by_details = SimpleAccountSerializer(source='created_by', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    assignment_count = serializers.SerializerMethodField()

    class Meta:
        model = Fee
        fields = [
            'id', 'organization', 'organization_name', 'event', 'event_title',
            'title', 'description', 'fee_type', 'amount', 'due_date', 'status',
            'created_by', 'created_by_details', 'assignment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_assignment_count(self, obj):
        return obj.assignments.count()

    def validate(self, data):
        amount = data.get('amount', getattr(self.instance, 'amount', None))
        organization = data.get('organization', getattr(self.instance, 'organization', None))
        event = data.get('event', getattr(self.instance, 'event', None))

        if amount is not None and amount <= 0:
            raise serializers.ValidationError("Fee amount must be greater than zero.")
        if event and organization and event.organization_id != organization.id:
            raise serializers.ValidationError("Fee event must belong to the selected organization.")
        return data

class FeeAssignmentSerializer(serializers.ModelSerializer):
    fee_details = FeeSerializer(source='fee', read_only=True)
    user_details = SimpleAccountSerializer(source='user', read_only=True)
    balance = serializers.ReadOnlyField()

    class Meta:
        model = FeeAssignment
        fields = [
            'id', 'fee', 'fee_details', 'user', 'user_details',
            'amount_due', 'amount_paid', 'balance', 'status', 'due_date',
            'notes', 'assigned_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = ['amount_paid', 'assigned_at', 'updated_at', 'paid_at']
        extra_kwargs = {
            'amount_due': {'required': False},
            'due_date': {'required': False},
        }

    def validate(self, data):
        amount_due = data.get('amount_due', getattr(self.instance, 'amount_due', None))
        fee = data.get('fee', getattr(self.instance, 'fee', None))
        assignment_user = data.get('user', getattr(self.instance, 'user', None))

        if amount_due is not None and amount_due <= 0:
            raise serializers.ValidationError("Amount due must be greater than zero.")
        if fee and assignment_user and not is_member_for_serializer(assignment_user, fee.organization):
            raise serializers.ValidationError("Fees can only be assigned to organization members.")
        return data

class PaymentSerializer(serializers.ModelSerializer):
    assignment_details = FeeAssignmentSerializer(source='assignment', read_only=True)
    received_by_details = SimpleAccountSerializer(source='received_by', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'assignment', 'assignment_details', 'amount', 'payment_method',
            'reference_number', 'proof', 'paid_at', 'received_by',
            'received_by_details', 'notes', 'created_at'
        ]
        read_only_fields = ['received_by', 'created_at']

    def validate_proof(self, value):
        return validate_receipt_file(value)

    def validate(self, data):
        amount = data.get('amount', getattr(self.instance, 'amount', None))
        if amount is not None and amount <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return data

class PaymentSummarySerializer(serializers.Serializer):
    total_due = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    unpaid_count = serializers.IntegerField()
    partial_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    waived_count = serializers.IntegerField()

# --- Announcement Serializers ---

class AnnouncementSerializer(serializers.ModelSerializer):
    author_details = SimpleAccountSerializer(source='author', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_acronym = serializers.CharField(source='organization.acronym', read_only=True)
    is_system_wide = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            'id', 'organization', 'organization_name', 'organization_acronym',
            'title', 'content', 'author', 'author_details', 'is_pinned',
            'is_published', 'is_system_wide', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_is_system_wide(self, obj):
        return obj.organization is None

class NotificationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_acronym = serializers.CharField(source='organization.acronym', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'organization', 'organization_name',
            'organization_acronym', 'notification_type', 'title', 'message',
            'link', 'is_read', 'created_at', 'read_at'
        ]
        read_only_fields = ['created_at', 'read_at']

# --- Budget Serializers ---

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'is_income']

class BudgetSerializer(serializers.ModelSerializer):
    created_by_details = SimpleAccountSerializer(source='created_by', read_only=True)
    category_details = BudgetCategorySerializer(source='category', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'organization', 'organization_name', 'transaction_type',
            'category', 'category_details', 'amount', 'description', 'date',
            'receipt', 'created_by', 'created_by_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_receipt(self, value):
        return validate_receipt_file(value)

    def validate(self, data):
        amount = data.get('amount', getattr(self.instance, 'amount', None))
        category = data.get('category', getattr(self.instance, 'category', None))
        transaction_type = data.get('transaction_type', getattr(self.instance, 'transaction_type', None))

        if amount is not None and amount <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        if category and transaction_type:
            category_type = 'income' if category.is_income else 'expense'
            if category_type != transaction_type:
                raise serializers.ValidationError("Budget category type must match the transaction type.")
        return data

class BudgetSummarySerializer(serializers.Serializer):
    """Serializer for budget summary data"""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()

# --- Document Serializers ---

class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description']

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_details = SimpleAccountSerializer(source='uploaded_by', read_only=True)
    category_details = DocumentCategorySerializer(source='category', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    file_size = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = [
            'id', 'organization', 'organization_name', 'category', 'category_details',
            'title', 'description', 'file', 'file_size', 'file_extension',
            'visibility', 'uploaded_by', 'uploaded_by_details', 'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at', 'updated_at']

    def validate_file(self, value):
        return validate_document_file(value)

# --- Statistics Serializers ---

class AdminDashboardStatsSerializer(serializers.Serializer):
    """Admin dashboard statistics"""
    total_organizations = serializers.IntegerField()
    active_organizations = serializers.IntegerField()
    pending_organizations = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_events = serializers.IntegerField()
    total_members = serializers.IntegerField()

class OfficerDashboardStatsSerializer(serializers.Serializer):
    """Officer dashboard statistics for their organization"""
    member_count = serializers.IntegerField()
    officer_count = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    total_budget_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_budget_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    budget_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    document_count = serializers.IntegerField()
    unpaid_fee_assignments = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()

class OrganizationReportSerializer(serializers.Serializer):
    organization_id = serializers.IntegerField()
    organization_name = serializers.CharField()
    member_count = serializers.IntegerField()
    officer_count = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    total_events = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()
    total_attendance = serializers.IntegerField()
    total_registrations = serializers.IntegerField()
    total_budget_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_budget_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    budget_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fees_due = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_fees_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_fees = serializers.DecimalField(max_digits=12, decimal_places=2)
    document_count = serializers.IntegerField()


def is_member_for_serializer(user, organization):
    if not user or not organization:
        return False
    if organization.leader_id == user.id:
        return True
    return Membership.objects.filter(user=user, organization=organization, is_active=True).exists()
