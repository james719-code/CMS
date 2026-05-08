from rest_framework import permissions
from .models import Membership, Organization

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users (OSA).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsLeader(permissions.BasePermission):
    """
    Permission to only allow leaders of an organization.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'led_organization')

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'leader'):
            return obj.leader == request.user
        elif hasattr(obj, 'organization'):
            return obj.organization.leader == request.user
        return False

class IsOfficer(permissions.BasePermission):
    """
    Permission to allow officers of an organization.
    """
    def has_permission(self, request, view):
        return Membership.objects.filter(
            user=request.user, 
            role='officer', 
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        org = None
        if hasattr(obj, 'leader'):
            org = obj
        elif hasattr(obj, 'organization'):
            org = obj.organization
        
        if org:
            return Membership.objects.filter(
                user=request.user, 
                organization=org, 
                role='officer', 
                is_active=True
            ).exists()
        return False

class IsLeaderOrOfficer(permissions.BasePermission):
    """
    Permission to allow leaders or officers of an organization.
    """
    def has_object_permission(self, request, view, obj):
        org = None
        if hasattr(obj, 'leader'):
            org = obj
        elif hasattr(obj, 'organization'):
            org = obj.organization
        
        if not org:
            return False

        # Check if leader
        if org.leader == request.user:
            return True
        
        # Check if officer
        return Membership.objects.filter(
            user=request.user, 
            organization=org, 
            role='officer', 
            is_active=True
        ).exists()

class IsOfficerOrReadOnly(permissions.BasePermission):
    """
    Allow read access to anyone, but write access only to officers.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return Membership.objects.filter(
            user=request.user, 
            role='officer', 
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        org = None
        if hasattr(obj, 'leader'):
            org = obj
        elif hasattr(obj, 'organization'):
            org = obj.organization
        
        if org:
            return Membership.objects.filter(
                user=request.user, 
                organization=org, 
                role='officer', 
                is_active=True
            ).exists()
        return False

class IsMember(permissions.BasePermission):
    """
    Permission to allow members of an organization.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        org = None
        if hasattr(obj, 'leader'):
            org = obj
        elif hasattr(obj, 'organization'):
            org = obj.organization
            
        if org:
            return Membership.objects.filter(
                user=request.user, 
                organization=org, 
                is_active=True
            ).exists()
        return False

class IsMemberOrReadOnly(permissions.BasePermission):
    """
    Allow read access to anyone, but object-level checks for members.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        org = None
        if hasattr(obj, 'leader'):
            org = obj
        elif hasattr(obj, 'organization'):
            org = obj.organization
            
        if org:
            # Leader always has access
            if org.leader == request.user:
                return True
            # Check membership
            return Membership.objects.filter(
                user=request.user, 
                organization=org, 
                is_active=True
            ).exists()
        return True

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow object owners or admins.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'uploaded_by'):
            return obj.uploaded_by == request.user
        
        return False

def is_org_officer_or_leader(user, organization):
    """
    Utility function to check if user is an officer or leader of an organization.
    """
    if not user or not user.is_authenticated or not organization:
        return False
    if user.is_staff:
        return True
    if organization.leader == user:
        return True
    return Membership.objects.filter(
        user=user, 
        organization=organization, 
        role='officer', 
        is_active=True
    ).exists()

def is_org_member(user, organization):
    """
    Utility function to check if user is a member of an organization.
    """
    if not user or not user.is_authenticated or not organization:
        return False
    if user.is_staff:
        return True
    if organization.leader == user:
        return True
    return Membership.objects.filter(
        user=user, 
        organization=organization, 
        is_active=True
    ).exists()
