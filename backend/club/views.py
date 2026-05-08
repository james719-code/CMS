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
    ActivityCategory
)
from .serializers import (
    AccountSerializer, SimpleAccountSerializer, DepartmentSerializer, ProgramSerializer,
    OrganizationSerializer, OrganizationRegistrationSerializer, OrganizationListSerializer,
    MembershipSerializer, MembershipRequestSerializer,
    EventSerializer, EventListSerializer, AttendanceSerializer, ActivityCategorySerializer,
    AnnouncementSerializer, BudgetSerializer, BudgetCategorySerializer, BudgetSummarySerializer,
    DocumentSerializer, DocumentCategorySerializer,
    AdminDashboardStatsSerializer, OfficerDashboardStatsSerializer
)
from .permissions import (
    IsAdmin, IsLeader, IsOfficer, IsLeaderOrOfficer, 
    IsOfficerOrReadOnly, IsMember, IsOwnerOrAdmin,
    is_org_officer_or_leader, is_org_member
)

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
        return Response({'status': 'organization approved', 'organization': OrganizationSerializer(org).data})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        org = self.get_object()
        org.status = 'rejected'
        org.reviewed_by = request.user
        org.reviewed_at = timezone.now()
        org.status_note = request.data.get('reason', '')
        org.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'status_note', 'updated_at'])
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

# --- Attendance ViewSet ---

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
        
        serializer.save(author=self.request.user)

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
    }
    return Response(OfficerDashboardStatsSerializer(data).data)
