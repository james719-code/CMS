from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Organization
from ..serializers import OrganizationSerializer
from ..decorators import admin_required

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@admin_required
def insert_organization(request):
    serializer = OrganizationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_organizations(request):
    organizations = Organization.objects.all()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@admin_required
def update_organization(request, organization_id):
    try:
        organization = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrganizationSerializer(organization, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Organization updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@admin_required
def delete_organization(request, organization_id):
    try:
        organization = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

    organization.delete()
    return Response({'message': 'Organization deleted successfully'})