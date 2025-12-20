from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Account, Admin, Department, Program, Year, Section, Organization,
    Member, Officer, Activity, Attendance, Item, Merchandise, File
)
from .serializers import (
    AccountSerializer, DepartmentSerializer, ProgramSerializer, YearSerializer, 
    SectionSerializer, OrganizationSerializer, MemberSerializer, OfficerSerializer,
    ActivitySerializer, AttendanceSerializer, ItemSerializer, MerchandiseSerializer,
    FileSerializer, AdminSerializer
)
from .permissions import IsAdmin, IsOfficer, IsOfficerOfOrg, IsMemberOfOrg, IsOwnerOrReadOnly

# --- Authentication Views ---

class RegisterView(generics.CreateAPIView):
    queryset = Account.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = AccountSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra responses to the login data
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['name'] = self.user.name
        data['id'] = self.user.id
        
        # Determine roles
        data['is_staff'] = self.user.is_staff
        data['is_admin'] = Admin.objects.filter(account=self.user).exists()
        
        # Get Officer roles
        officer_orgs = Officer.objects.filter(account=self.user).values_list('organization__id', flat=True)
        data['officer_of'] = list(officer_orgs)
        
        # Get Member roles
        member_orgs = Member.objects.filter(account=self.user).values_list('organization__id', flat=True)
        data['member_of'] = list(member_orgs)

        return data

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# --- ViewSets ---

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated] # Simplified for now, refine later if needed

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department']

class YearViewSet(viewsets.ModelViewSet):
    queryset = Year.objects.all()
    serializer_class = YearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['program']

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['year']

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsOfficerOfOrg()]
        return [IsAuthenticated()]

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAdmin]

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'account']

    def get_queryset(self):
        user = self.request.user
        if Admin.objects.filter(account=user).exists():
            return Member.objects.all()
        
        # Officers can see members of their orgs
        officer_orgs = Officer.objects.filter(account=user).values_list('organization', flat=True)
        # Members can see themselves
        return Member.objects.filter(organization__in=officer_orgs) | Member.objects.filter(account=user)

    def perform_create(self, serializer):
        # Only Admins or Officers of the org can create members
        org = serializer.validated_data['organization']
        user = self.request.user
        if not (Admin.objects.filter(account=user).exists() or 
                Officer.objects.filter(account=user, organization=org).exists()):
             raise serializers.ValidationError("You do not have permission to add members to this organization.")
        serializer.save()

class OfficerViewSet(viewsets.ModelViewSet):
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization']

    def get_queryset(self):
        # Similar logic to members, but maybe stricter?
        return Officer.objects.all()

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOfficerOfOrg()]
        return [IsAuthenticated()]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity', 'member']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOfficerOfOrg()] # Need to check the activity's org
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Check permission against the activity's organization
        activity = serializer.validated_data['activity']
        user = self.request.user
        if not (Admin.objects.filter(account=user).exists() or 
                Officer.objects.filter(account=user, organization=activity.organization).exists()):
             raise serializers.ValidationError("You do not have permission to take attendance for this activity.")
        serializer.save()

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity']

class MerchandiseViewSet(viewsets.ModelViewSet):
    queryset = Merchandise.objects.all()
    serializer_class = MerchandiseSerializer
    permission_classes = [IsAuthenticated]

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOfficerOfOrg()]
        return [IsAuthenticated()]
