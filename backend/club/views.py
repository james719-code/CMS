from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from django.utils import timezone

from .models import (
    Account, Department, Program, Organization,
    Membership, MembershipRequest, Event, Attendance,
    Announcement, Budget, BudgetCategory, Document, DocumentCategory,
    ActivityCategory, EventRegistration, Fee, FeeAssignment, Payment,
    Notification
)
from .serializers import (
    AccountSerializer, SimpleAccountSerializer, DepartmentSerializer, ProgramSerializer,
    OrganizationSerializer, OrganizationRegistrationSerializer, OrganizationListSerializer,
    MembershipSerializer, MembershipRequestSerializer,
    EventSerializer, EventListSerializer, AttendanceSerializer, ActivityCategorySerializer,
    AnnouncementSerializer, BudgetSerializer, BudgetCategorySerializer, BudgetSummarySerializer,
    DocumentSerializer, DocumentCategorySerializer,
    AdminDashboardStatsSerializer, OfficerDashboardStatsSerializer,
    EventRegistrationSerializer, FeeSerializer, FeeAssignmentSerializer,
    PaymentSerializer, PaymentSummarySerializer, NotificationSerializer,
    OrganizationReportSerializer
)
from .permissions import (
    IsAdmin, IsLeader, IsOfficer, IsLeaderOrOfficer, 
    IsOfficerOrReadOnly, IsMember, IsOwnerOrAdmin,
    is_org_officer_or_leader, is_org_member
)


def user_officer_org_ids(user):
    org_ids = list(Membership.objects.filter(
        user=user,
        role='officer',
        is_active=True,
    ).values_list('organization_id', flat=True))

    led_org_id = getattr(getattr(user, 'led_organization', None), 'id', None)
    if led_org_id:
        org_ids.append(led_org_id)
    return list(set(org_ids))


def notify_users(users, title, message='', notification_type='system', organization=None, link=''):
    notifications = [
        Notification(
            recipient=user,
            organization=organization,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        for user in users
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)

# --- Authentication Views ---

class RegisterView(generics.CreateAPIView):
    queryset = Account.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = AccountSerializer
    throttle_scope = 'auth'

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['id'] = self.user.id
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['is_staff'] = self.user.is_staff
        
        # Check if user leads any org
        try:
            org = self.user.led_organization
            data['led_org_id'] = org.id
            data['led_org_status'] = org.status
            data['led_org_name'] = org.name
        except Organization.DoesNotExist:
            data['led_org_id'] = None
            data['led_org_status'] = None
            data['led_org_name'] = None

        # Get officer organizations
        officer_memberships = Membership.objects.filter(
            user=self.user, role='officer', is_active=True
        ).select_related('organization')
        data['officer_orgs'] = [
            {'id': m.organization.id, 'name': m.organization.name, 'acronym': m.organization.acronym}
            for m in officer_memberships
        ]

        return data

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = 'auth'


class CustomTokenRefreshView(TokenRefreshView):
    throttle_scope = 'auth'

# --- Account ViewSet ---

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related('program', 'program__department')
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'student_id']
    filterset_fields = ['program', 'year_level', 'is_active', 'is_staff']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined']

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data)

# --- Core Academic ViewSets ---

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.prefetch_related('programs')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'initials', 'description']
    ordering_fields = ['name', 'initials']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related('department')
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department']
    search_fields = ['name', 'description', 'department__name']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

# --- Organization ViewSet ---

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related('leader', 'reviewed_by').prefetch_related('members')
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'acronym']
    ordering_fields = ['name', 'created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationListSerializer
        return OrganizationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(Q(status='active') | Q(leader=user))

    def perform_create(self, serializer):
        user = self.request.user
        if Organization.objects.filter(leader=user).exists():
            raise ValidationError("You are already leading an organization.")
        org = serializer.save(leader=user, status='pending')
        Membership.objects.get_or_create(
            user=user,
            organization=org,
            defaults={'role': 'officer', 'position': 'President', 'role_changed_by': user, 'role_changed_at': timezone.now()}
        )

    def perform_update(self, serializer):
        org = self.get_object()
        if not self.request.user.is_staff and org.leader != self.request.user:
            raise PermissionDenied("Only the organization leader or an admin can update this organization.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can delete organizations.")
        instance.delete()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request):
        serializer = OrganizationRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            org = serializer.save(leader=request.user, status='pending')
            Membership.objects.create(
                user=request.user,
                organization=org,
                role='officer',
                position='President',
                role_changed_by=request.user,
                role_changed_at=timezone.now()
            )
            return Response(OrganizationSerializer(org).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        org = self.get_object()
        org.status = 'active'
        org.reviewed_by = request.user
        org.reviewed_at = timezone.now()
        org.status_note = request.data.get('note', '')
        org.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'status_note', 'updated_at'])
        notify_users([org.leader], f"{org.name} approved", org.status_note, notification_type='membership', organization=org, link=f"/organizations/{org.id}")
        return Response({'status': 'organization approved', 'organization': OrganizationSerializer(org).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        org = self.get_object()
        org.status = 'rejected'
        org.reviewed_by = request.user
        org.reviewed_at = timezone.now()
        org.status_note = request.data.get('reason', '')
        org.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'status_note', 'updated_at'])
        notify_users([org.leader], f"{org.name} rejected", org.status_note, notification_type='membership', organization=org, link=f"/organizations/{org.id}")
        return Response({'status': 'organization rejected'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def suspend(self, request, pk=None):
        org = self.get_object()
        org.status = 'suspended'
        org.reviewed_by = request.user
        org.reviewed_at = timezone.now()
        org.status_note = request.data.get('reason', '')
        org.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'status_note', 'updated_at'])
        return Response({'status': 'organization suspended'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reactivate(self, request, pk=None):
        org = self.get_object()
        org.status = 'active'
        org.reviewed_by = request.user
        org.reviewed_at = timezone.now()
        org.status_note = request.data.get('note', '')
        org.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'status_note', 'updated_at'])
        return Response({'status': 'organization reactivated'})

# --- Membership ViewSet ---

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.select_related('user', 'organization', 'role_changed_by')
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'user', 'role', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['date_joined', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        
        # Get memberships of orgs user is officer/leader of, or their own
        officer_orgs = Membership.objects.filter(
            user=user, role='officer', is_active=True
        ).values_list('organization_id', flat=True)
        
        led_org_id = getattr(getattr(user, 'led_organization', None), 'id', None)
        if led_org_id:
            officer_orgs = list(officer_orgs) + [led_org_id]
        
        return self.queryset.filter(
            Q(organization_id__in=officer_orgs) | Q(user=user)
        )

    def perform_create(self, serializer):
        org = serializer.validated_data['organization']
        if org.status != 'active' and not self.request.user.is_staff:
            raise ValidationError("Members can only be added to active organizations.")
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only organization officers can add members.")
        serializer.save(role='member', position='', is_active=True)

    def perform_update(self, serializer):
        membership = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, membership.organization):
            raise PermissionDenied("Only organization officers can update memberships.")
        if 'user' in serializer.validated_data or 'organization' in serializer.validated_data:
            raise ValidationError("Membership user and organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.organization):
            raise PermissionDenied("Only organization officers can delete memberships.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def promote(self, request, pk=None):
        membership = self.get_object()
        org = membership.organization
        
        if not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        membership.role = 'officer'
        membership.position = request.data.get('position', '')
        membership.role_changed_by = request.user
        membership.role_changed_at = timezone.now()
        membership.save(update_fields=['role', 'position', 'role_changed_by', 'role_changed_at', 'updated_at'])
        return Response(MembershipSerializer(membership).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def demote(self, request, pk=None):
        membership = self.get_object()
        org = membership.organization
        
        if org.leader != request.user and not request.user.is_staff:
            return Response({'error': 'Only the leader can demote officers'}, status=status.HTTP_403_FORBIDDEN)
        
        membership.role = 'member'
        membership.position = ''
        membership.role_changed_by = request.user
        membership.role_changed_at = timezone.now()
        membership.save(update_fields=['role', 'position', 'role_changed_by', 'role_changed_at', 'updated_at'])
        return Response(MembershipSerializer(membership).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        membership = self.get_object()
        org = membership.organization
        
        if not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        membership.is_active = False
        membership.role_changed_by = request.user
        membership.role_changed_at = timezone.now()
        membership.save(update_fields=['is_active', 'role_changed_by', 'role_changed_at', 'updated_at'])
        return Response({'status': 'membership deactivated'})

# --- Membership Request ViewSet ---

class MembershipRequestViewSet(viewsets.ModelViewSet):
    queryset = MembershipRequest.objects.select_related('user', 'organization', 'reviewed_by')
    serializer_class = MembershipRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'user', 'status']
    ordering_fields = ['created_at', 'reviewed_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        
        # Get requests for orgs user is officer/leader of, or their own
        officer_orgs = Membership.objects.filter(
            user=user, role='officer', is_active=True
        ).values_list('organization_id', flat=True)
        
        led_org_id = getattr(getattr(user, 'led_organization', None), 'id', None)
        if led_org_id:
            officer_orgs = list(officer_orgs) + [led_org_id]
        
        return self.queryset.filter(
            Q(organization_id__in=officer_orgs) | Q(user=user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        membership_request = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, membership_request.organization):
            raise PermissionDenied("Only organization officers can update membership requests.")
        if 'organization' in serializer.validated_data:
            raise ValidationError("Membership request organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.user != self.request.user:
            raise PermissionDenied("Only the requester or an admin can delete this request.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        membership_request = self.get_object()
        org = membership_request.organization
        
        if not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if membership_request.status != 'pending':
            return Response({'error': 'Request already processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create membership
        membership, _ = Membership.objects.get_or_create(
            user=membership_request.user,
            organization=org,
            defaults={'role': 'member'}
        )
        if not membership.is_active:
            membership.is_active = True
            membership.save(update_fields=['is_active', 'updated_at'])
        
        membership_request.status = 'approved'
        membership_request.reviewed_by = request.user
        membership_request.reviewed_at = timezone.now()
        membership_request.save()
        notify_users(
            [membership_request.user],
            f"Membership approved for {org.acronym}",
            notification_type='membership',
            organization=org,
            link=f"/organizations/{org.id}",
        )
        
        return Response({'status': 'request approved', 'request': MembershipRequestSerializer(membership_request).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        membership_request = self.get_object()
        org = membership_request.organization
        
        if not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if membership_request.status != 'pending':
            return Response({'error': 'Request already processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        membership_request.status = 'rejected'
        membership_request.reviewed_by = request.user
        membership_request.reviewed_at = timezone.now()
        membership_request.rejection_reason = request.data.get('reason', '')
        membership_request.save()
        notify_users(
            [membership_request.user],
            f"Membership rejected for {org.acronym}",
            membership_request.rejection_reason,
            notification_type='membership',
            organization=org,
            link=f"/organizations/{org.id}",
        )
        
        return Response({'status': 'request rejected'})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        org_id = request.query_params.get('organization')
        if not org_id:
            return Response({'error': 'organization parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        requests = self.get_queryset().filter(organization_id=org_id, status='pending')
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = MembershipRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(MembershipRequestSerializer(requests, many=True).data)

# --- Event ViewSet ---

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('organization', 'category')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'category', 'is_open_for_non_members']
    search_fields = ['title', 'description', 'venue']
    ordering_fields = ['start_time', 'end_time', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.all()
        
        # Filter upcoming events
        if self.request.query_params.get('upcoming') == 'true':
            qs = qs.filter(start_time__gte=timezone.now())
        
        # Filter past events
        if self.request.query_params.get('past') == 'true':
            qs = qs.filter(end_time__lt=timezone.now())
        
        return qs

    def perform_create(self, serializer):
        org = serializer.validated_data['organization']
        if org.status != 'active':
            raise ValidationError("Events can only be created for active organizations.")
        if not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can create events.")
        serializer.save()

    def perform_update(self, serializer):
        org = serializer.instance.organization
        if not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can update events.")
        if 'organization' in serializer.validated_data:
            raise ValidationError("Event organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.organization):
            raise PermissionDenied("Only officers can delete events.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def my_events(self, request):
        """Get events for organizations user is a member of"""
        user = request.user
        member_orgs = Membership.objects.filter(user=user, is_active=True).values_list('organization_id', flat=True)
        events = Event.objects.filter(
            Q(organization_id__in=member_orgs) | Q(is_open_for_non_members=True)
        ).filter(start_time__gte=timezone.now()).order_by('start_time')
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = EventListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(EventListSerializer(events, many=True).data)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        registration_user_id = request.data.get('user', request.user.id)

        try:
            registration_user = Account.objects.get(id=registration_user_id)
        except Account.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if registration_user != request.user and not is_org_officer_or_leader(request.user, event.organization):
            return Response({'error': 'Only officers can register other users'}, status=status.HTTP_403_FORBIDDEN)
        if event.end_time < timezone.now():
            return Response({'error': 'Registration is closed for past events'}, status=status.HTTP_400_BAD_REQUEST)
        if event.registration_deadline and event.registration_deadline < timezone.now():
            return Response({'error': 'Registration deadline has passed'}, status=status.HTTP_400_BAD_REQUEST)
        if not event.is_open_for_non_members and not is_org_member(registration_user, event.organization):
            return Response({'error': 'Only members can register for this event'}, status=status.HTTP_403_FORBIDDEN)

        registration, created = EventRegistration.objects.get_or_create(
            event=event,
            user=registration_user,
            defaults={
                'status': 'waitlisted' if event.is_registration_full else 'registered',
                'notes': request.data.get('notes', ''),
            }
        )
        if not created and registration.status == 'cancelled':
            registration.status = 'waitlisted' if event.is_registration_full else 'registered'
            registration.cancelled_at = None
            registration.notes = request.data.get('notes', registration.notes)
            registration.save(update_fields=['status', 'cancelled_at', 'notes', 'updated_at'])
        elif not created:
            return Response({'error': 'Already registered for this event'}, status=status.HTTP_400_BAD_REQUEST)

        notify_users(
            [registration_user],
            f"Registered for {event.title}" if registration.status == 'registered' else f"Waitlisted for {event.title}",
            notification_type='event',
            organization=event.organization,
            link=f"/events/{event.id}",
        )
        return Response(EventRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)

# --- Attendance ViewSet ---

class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.select_related('event', 'event__organization', 'user')
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'user', 'status']
    ordering_fields = ['registered_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()

        officer_orgs = user_officer_org_ids(user)
        return self.queryset.filter(
            Q(event__organization_id__in=officer_orgs) | Q(user=user)
        )

    def perform_create(self, serializer):
        event = serializer.validated_data['event']
        registration_user = serializer.validated_data.get('user', self.request.user)

        if registration_user != self.request.user and not is_org_officer_or_leader(self.request.user, event.organization):
            raise PermissionDenied("Only officers can register other users.")
        registration_status = 'waitlisted' if event.is_registration_full else 'registered'
        registration = serializer.save(user=registration_user, status=registration_status)
        notify_users(
            [registration_user],
            f"Registered for {event.title}" if registration.status == 'registered' else f"Waitlisted for {event.title}",
            notification_type='event',
            organization=event.organization,
            link=f"/events/{event.id}",
        )

    def perform_update(self, serializer):
        registration = self.get_object()
        if registration.user != self.request.user and not is_org_officer_or_leader(self.request.user, registration.event.organization):
            raise PermissionDenied("Only officers can update registrations for other users.")
        if 'event' in serializer.validated_data or 'user' in serializer.validated_data:
            raise ValidationError("Registration event and user cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and instance.user != self.request.user and not is_org_officer_or_leader(self.request.user, instance.event.organization):
            raise PermissionDenied("Only the registrant or organization officers can delete this registration.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        registration = self.get_object()
        if registration.user != request.user and not is_org_officer_or_leader(request.user, registration.event.organization):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if registration.status == 'cancelled':
            return Response({'error': 'Registration already cancelled'}, status=status.HTTP_400_BAD_REQUEST)

        registration.status = 'cancelled'
        registration.cancelled_at = timezone.now()
        registration.save(update_fields=['status', 'cancelled_at', 'updated_at'])
        return Response(EventRegistrationSerializer(registration).data)

    @action(detail=True, methods=['post'])
    def approve_waitlist(self, request, pk=None):
        registration = self.get_object()
        if not is_org_officer_or_leader(request.user, registration.event.organization):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if registration.status != 'waitlisted':
            return Response({'error': 'Only waitlisted registrations can be approved'}, status=status.HTTP_400_BAD_REQUEST)
        if registration.event.is_registration_full:
            return Response({'error': 'Event registration is already full'}, status=status.HTTP_400_BAD_REQUEST)

        registration.status = 'registered'
        registration.cancelled_at = None
        registration.save(update_fields=['status', 'cancelled_at', 'updated_at'])
        notify_users(
            [registration.user],
            f"Waitlist approved for {registration.event.title}",
            notification_type='event',
            organization=registration.event.organization,
            link=f"/events/{registration.event.id}",
        )
        return Response(EventRegistrationSerializer(registration).data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('event', 'event__organization', 'user', 'checked_in_by')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'user']
    ordering_fields = ['time_in', 'time_out']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        
        # Get attendance for events of orgs user is officer/leader of, or their own
        officer_orgs = Membership.objects.filter(
            user=user, role='officer', is_active=True
        ).values_list('organization_id', flat=True)
        
        led_org_id = getattr(getattr(user, 'led_organization', None), 'id', None)
        if led_org_id:
            officer_orgs = list(officer_orgs) + [led_org_id]
        
        return self.queryset.filter(
            Q(event__organization_id__in=officer_orgs) | Q(user=user)
        )

    def perform_create(self, serializer):
        event = serializer.validated_data['event']
        attendance_user = serializer.validated_data.get('user', self.request.user)
        if attendance_user != self.request.user and not is_org_officer_or_leader(self.request.user, event.organization):
            raise PermissionDenied("Only officers can record attendance for other users.")
        if not event.is_open_for_non_members and not is_org_member(attendance_user, event.organization):
            raise PermissionDenied("Only members can attend this event.")
        if event.is_full:
            raise ValidationError("Event is already full.")
        serializer.save(checked_in_by=self.request.user)

    def perform_update(self, serializer):
        attendance = self.get_object()
        if attendance.user != self.request.user and not is_org_officer_or_leader(self.request.user, attendance.event.organization):
            raise PermissionDenied("Only officers can update attendance for other users.")
        if 'event' in serializer.validated_data or 'user' in serializer.validated_data:
            raise ValidationError("Attendance event and user cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.event.organization):
            raise PermissionDenied("Only officers can delete attendance records.")
        instance.delete()

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        event_id = request.data.get('event')
        user_id = request.data.get('user', request.user.id)
        
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            attendance_user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Permission check - only officers can check in others
        if str(user_id) != str(request.user.id) and not is_org_officer_or_leader(request.user, event.organization):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if not event.is_open_for_non_members and not is_org_member(attendance_user, event.organization):
            return Response({'error': 'Only members can attend this event'}, status=status.HTTP_403_FORBIDDEN)
        if event.is_full:
            return Response({'error': 'Event is already full'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance, created = Attendance.objects.get_or_create(
            event_id=event_id,
            user_id=user_id,
            defaults={'time_in': timezone.now(), 'checked_in_by': request.user}
        )
        
        if not created:
            return Response({'error': 'Already checked in'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        attendance = self.get_object()
        if attendance.time_out:
            return Response({'error': 'Already checked out'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.time_out = timezone.now()
        attendance.save()
        return Response(AttendanceSerializer(attendance).data)

# --- Activity Category ViewSet ---

class ActivityCategoryViewSet(viewsets.ModelViewSet):
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

# --- Announcement ViewSet ---

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.select_related('organization', 'author')
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'is_pinned', 'is_published']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        
        # Get org filter
        org_id = self.request.query_params.get('organization')
        
        if user.is_staff:
            qs = Announcement.objects.all()
        else:
            # Get member orgs
            member_orgs = Membership.objects.filter(user=user, is_active=True).values_list('organization_id', flat=True)
            
            # Show system-wide announcements + announcements from member orgs
            qs = Announcement.objects.filter(
                Q(organization__isnull=True) | Q(organization_id__in=member_orgs)
            ).filter(is_published=True)
        
        if org_id:
            if org_id == 'system':
                qs = qs.filter(organization__isnull=True)
            else:
                qs = qs.filter(organization_id=org_id)
        
        return qs

    def perform_create(self, serializer):
        org = serializer.validated_data.get('organization')
        
        # Only admins can create system-wide announcements
        if org is None and not self.request.user.is_staff:
            raise PermissionDenied("Only admins can create system-wide announcements.")
        
        # Only officers can create org announcements
        if org and not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can create announcements.")
        
        announcement = serializer.save(author=self.request.user)
        if announcement.organization:
            recipients = Account.objects.filter(
                memberships__organization=announcement.organization,
                memberships__is_active=True,
            ).distinct()
            notify_users(
                recipients,
                announcement.title,
                notification_type='announcement',
                organization=announcement.organization,
                link=f"/announcements/{announcement.id}",
            )
        else:
            notify_users(
                Account.objects.filter(is_active=True),
                announcement.title,
                notification_type='announcement',
                link=f"/announcements/{announcement.id}",
            )

    def perform_update(self, serializer):
        announcement = self.get_object()
        org = announcement.organization
        if org is None and not self.request.user.is_staff:
            raise PermissionDenied("Only admins can update system-wide announcements.")
        if org and not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can update announcements.")
        if 'organization' in serializer.validated_data:
            raise ValidationError("Announcement organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        org = instance.organization
        if org is None and not self.request.user.is_staff:
            raise PermissionDenied("Only admins can delete system-wide announcements.")
        if org and not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can delete announcements.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        announcement = self.get_object()
        org = announcement.organization
        
        if org and not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if org is None and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        announcement.is_pinned = True
        announcement.save()
        return Response(AnnouncementSerializer(announcement).data)

    @action(detail=True, methods=['post'])
    def unpin(self, request, pk=None):
        announcement = self.get_object()
        org = announcement.organization
        
        if org and not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if org is None and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        announcement.is_pinned = False
        announcement.save()
        return Response(AnnouncementSerializer(announcement).data)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('recipient', 'organization')
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'notification_type', 'is_read']
    ordering_fields = ['created_at', 'read_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return self.queryset.all()
        return self.queryset.filter(recipient=user)

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can create direct notifications.")
        serializer.save()

    def perform_update(self, serializer):
        notification = self.get_object()
        if notification.recipient != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only update your own notifications.")
        serializer.save(read_at=timezone.now() if serializer.validated_data.get('is_read') else notification.read_at)

    def perform_destroy(self, instance):
        if instance.recipient != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only delete your own notifications.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = False
        notification.read_at = None
        notification.save(update_fields=['is_read', 'read_at'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response({'updated': updated})

# --- Budget ViewSets ---

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('organization', 'category', 'created_by')
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'transaction_type', 'category']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        
        # Get budgets for orgs user is officer/leader of
        officer_orgs = Membership.objects.filter(
            user=user, role='officer', is_active=True
        ).values_list('organization_id', flat=True)
        
        led_org_id = getattr(getattr(user, 'led_organization', None), 'id', None)
        if led_org_id:
            officer_orgs = list(officer_orgs) + [led_org_id]
        
        return self.queryset.filter(organization_id__in=officer_orgs)

    def perform_create(self, serializer):
        org = serializer.validated_data['organization']
        if not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can manage budget.")
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        budget = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, budget.organization):
            raise PermissionDenied("Only officers can manage budget.")
        if 'organization' in serializer.validated_data:
            raise ValidationError("Budget organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.organization):
            raise PermissionDenied("Only officers can manage budget.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        org_id = request.query_params.get('organization')
        if not org_id:
            return Response({'error': 'organization parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user.is_staff and not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        budgets = Budget.objects.filter(organization_id=org_id)
        
        income = budgets.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = budgets.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        
        data = {
            'total_income': income,
            'total_expense': expense,
            'balance': income - expense,
            'transaction_count': budgets.count()
        }
        
        return Response(BudgetSummarySerializer(data).data)

# --- Dues & Payment ViewSets ---

class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.select_related('organization', 'event', 'created_by').prefetch_related('assignments')
    serializer_class = FeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'event', 'fee_type', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'amount']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()

        member_orgs = Membership.objects.filter(user=user, is_active=True).values_list('organization_id', flat=True)
        return self.queryset.filter(organization_id__in=member_orgs)

    def perform_create(self, serializer):
        org = serializer.validated_data['organization']
        if not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can create fees.")
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        fee = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, fee.organization):
            raise PermissionDenied("Only officers can update fees.")
        if 'organization' in serializer.validated_data:
            raise ValidationError("Fee organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.organization):
            raise PermissionDenied("Only officers can delete fees.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def assign_members(self, request, pk=None):
        fee = self.get_object()
        if not is_org_officer_or_leader(request.user, fee.organization):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        user_ids = request.data.get('user_ids')
        memberships = Membership.objects.filter(organization=fee.organization, is_active=True).select_related('user')
        if user_ids:
            memberships = memberships.filter(user_id__in=user_ids)

        created = 0
        assignments = []
        for membership in memberships:
            assignment, was_created = FeeAssignment.objects.get_or_create(
                fee=fee,
                user=membership.user,
                defaults={
                    'amount_due': fee.amount,
                    'due_date': fee.due_date,
                }
            )
            assignments.append(assignment)
            if was_created:
                created += 1

        notify_users(
            [assignment.user for assignment in assignments],
            f"New fee assigned: {fee.title}",
            f"Amount due: {fee.amount}",
            notification_type='payment',
            organization=fee.organization,
            link=f"/fees/{fee.id}",
        )
        return Response({
            'created': created,
            'total_assignments': len(assignments),
            'assignments': FeeAssignmentSerializer(assignments, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        org_id = request.query_params.get('organization')
        if not org_id:
            return Response({'error': 'organization parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff and not is_org_officer_or_leader(request.user, org):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        assignments = FeeAssignment.objects.filter(fee__organization=org)
        total_due = assignments.aggregate(total=Sum('amount_due'))['total'] or 0
        total_paid = assignments.aggregate(total=Sum('amount_paid'))['total'] or 0
        data = {
            'total_due': total_due,
            'total_paid': total_paid,
            'outstanding_balance': total_due - total_paid,
            'unpaid_count': assignments.filter(status='unpaid').count(),
            'partial_count': assignments.filter(status='partial').count(),
            'paid_count': assignments.filter(status='paid').count(),
            'waived_count': assignments.filter(status='waived').count(),
        }
        return Response(PaymentSummarySerializer(data).data)


class FeeAssignmentViewSet(viewsets.ModelViewSet):
    queryset = FeeAssignment.objects.select_related('fee', 'fee__organization', 'fee__event', 'user')
    serializer_class = FeeAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fee', 'user', 'status']
    ordering_fields = ['due_date', 'assigned_at', 'amount_due', 'amount_paid']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()

        officer_orgs = user_officer_org_ids(user)
        return self.queryset.filter(
            Q(fee__organization_id__in=officer_orgs) | Q(user=user)
        )

    def perform_create(self, serializer):
        fee = serializer.validated_data['fee']
        if not is_org_officer_or_leader(self.request.user, fee.organization):
            raise PermissionDenied("Only officers can assign fees.")
        serializer.save(
            amount_due=serializer.validated_data.get('amount_due') or fee.amount,
            due_date=serializer.validated_data.get('due_date') or fee.due_date,
        )

    def perform_update(self, serializer):
        assignment = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, assignment.fee.organization):
            raise PermissionDenied("Only officers can update fee assignments.")
        if 'fee' in serializer.validated_data or 'user' in serializer.validated_data:
            raise ValidationError("Assignment fee and user cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.fee.organization):
            raise PermissionDenied("Only officers can delete fee assignments.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def waive(self, request, pk=None):
        assignment = self.get_object()
        if not is_org_officer_or_leader(request.user, assignment.fee.organization):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        assignment.status = 'waived'
        assignment.notes = request.data.get('notes', assignment.notes)
        assignment.save(update_fields=['status', 'notes', 'updated_at'])
        return Response(FeeAssignmentSerializer(assignment).data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'assignment', 'assignment__fee', 'assignment__fee__organization',
        'assignment__user', 'received_by'
    )
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['assignment', 'payment_method']
    ordering_fields = ['paid_at', 'created_at', 'amount']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()

        officer_orgs = user_officer_org_ids(user)
        return self.queryset.filter(
            Q(assignment__fee__organization_id__in=officer_orgs) | Q(assignment__user=user)
        )

    def perform_create(self, serializer):
        assignment = serializer.validated_data['assignment']
        if not is_org_officer_or_leader(self.request.user, assignment.fee.organization):
            raise PermissionDenied("Only officers can record payments.")
        payment = serializer.save(received_by=self.request.user)
        payment.assignment.refresh_payment_status()
        notify_users(
            [payment.assignment.user],
            f"Payment recorded for {payment.assignment.fee.title}",
            f"Amount paid: {payment.amount}",
            notification_type='payment',
            organization=payment.assignment.fee.organization,
            link=f"/fee-assignments/{payment.assignment.id}",
        )

    def perform_update(self, serializer):
        payment = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, payment.assignment.fee.organization):
            raise PermissionDenied("Only officers can update payments.")
        if 'assignment' in serializer.validated_data:
            raise ValidationError("Payment assignment cannot be changed.")
        payment = serializer.save()
        payment.assignment.refresh_payment_status()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.assignment.fee.organization):
            raise PermissionDenied("Only officers can delete payments.")
        assignment = instance.assignment
        instance.delete()
        assignment.refresh_payment_status()

# --- Document ViewSets ---

class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('organization', 'category', 'uploaded_by')
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'category', 'visibility']
    search_fields = ['title', 'description']
    ordering_fields = ['uploaded_at', 'updated_at', 'title']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        
        # Get member orgs and officer orgs
        memberships = Membership.objects.filter(user=user, is_active=True)
        member_orgs = memberships.values_list('organization_id', flat=True)
        officer_orgs = memberships.filter(role='officer').values_list('organization_id', flat=True)
        
        led_org_id = getattr(getattr(user, 'led_organization', None), 'id', None)
        if led_org_id:
            officer_orgs = list(officer_orgs) + [led_org_id]
        
        # Members can see members-visible docs, officers can see all
        return self.queryset.filter(
            Q(organization_id__in=officer_orgs) |
            Q(organization_id__in=member_orgs, visibility__in=['members', 'public']) |
            Q(visibility='public')
        ).distinct()

    def perform_create(self, serializer):
        org = serializer.validated_data['organization']
        if not is_org_officer_or_leader(self.request.user, org):
            raise PermissionDenied("Only officers can upload documents.")
        serializer.save(uploaded_by=self.request.user)

    def perform_update(self, serializer):
        document = self.get_object()
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, document.organization):
            raise PermissionDenied("Only officers can update documents.")
        if 'organization' in serializer.validated_data:
            raise ValidationError("Document organization cannot be changed.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff and not is_org_officer_or_leader(self.request.user, instance.organization):
            raise PermissionDenied("Only officers can delete documents.")
        instance.delete()

# --- Dashboard Statistics Views ---

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_dashboard_stats(request):
    """Admin dashboard statistics"""
    data = {
        'total_organizations': Organization.objects.count(),
        'active_organizations': Organization.objects.filter(status='active').count(),
        'pending_organizations': Organization.objects.filter(status='pending').count(),
        'total_users': Account.objects.filter(is_active=True).count(),
        'total_events': Event.objects.count(),
        'total_members': Membership.objects.filter(is_active=True).count(),
    }
    return Response(AdminDashboardStatsSerializer(data).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def officer_dashboard_stats(request, org_id):
    """Officer dashboard statistics for an organization"""
    try:
        org = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not request.user.is_staff and not is_org_officer_or_leader(request.user, org):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    budgets = Budget.objects.filter(organization=org)
    income = budgets.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = budgets.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    
    data = {
        'member_count': org.member_count,
        'officer_count': org.officer_count,
        'pending_requests': MembershipRequest.objects.filter(organization=org, status='pending').count(),
        'upcoming_events': Event.objects.filter(organization=org, start_time__gte=timezone.now()).count(),
        'total_budget_income': income,
        'total_budget_expense': expense,
        'budget_balance': income - expense,
        'document_count': Document.objects.filter(organization=org).count(),
        'unpaid_fee_assignments': FeeAssignment.objects.filter(fee__organization=org, status__in=['unpaid', 'partial']).count(),
        'unread_notifications': Notification.objects.filter(recipient=request.user, is_read=False).count(),
    }
    return Response(OfficerDashboardStatsSerializer(data).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_report(request, org_id):
    """Operational report for officers: membership, events, attendance, finances, and documents."""
    try:
        org = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.is_staff and not is_org_officer_or_leader(request.user, org):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    budgets = Budget.objects.filter(organization=org)
    income = budgets.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = budgets.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0

    assignments = FeeAssignment.objects.filter(fee__organization=org)
    total_due = assignments.aggregate(total=Sum('amount_due'))['total'] or 0
    total_paid = assignments.aggregate(total=Sum('amount_paid'))['total'] or 0

    data = {
        'organization_id': org.id,
        'organization_name': org.name,
        'member_count': org.member_count,
        'officer_count': org.officer_count,
        'pending_requests': MembershipRequest.objects.filter(organization=org, status='pending').count(),
        'total_events': Event.objects.filter(organization=org).count(),
        'upcoming_events': Event.objects.filter(organization=org, start_time__gte=timezone.now()).count(),
        'total_attendance': Attendance.objects.filter(event__organization=org).count(),
        'total_registrations': EventRegistration.objects.filter(event__organization=org, status='registered').count(),
        'total_budget_income': income,
        'total_budget_expense': expense,
        'budget_balance': income - expense,
        'total_fees_due': total_due,
        'total_fees_paid': total_paid,
        'outstanding_fees': total_due - total_paid,
        'document_count': Document.objects.filter(organization=org).count(),
    }
    return Response(OrganizationReportSerializer(data).data)
