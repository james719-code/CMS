# views/admin.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers import AdminSerializer
from ..models import Admin
from ..decorators import admin_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from ..models import Account

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@admin_required
def insert_admin(request):
    serializer = AdminSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_admin(request):
    admins = Admin.objects.all()
    serializer = AdminSerializer(admins, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@admin_required
def update_admin(request, admin_id):
    try:
        admin = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AdminSerializer(admin, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@admin_required
def delete_admin(request, admin_id):
    try:
        admin = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

    admin.delete()
    admin.account.delete()  # Assuming you want to delete the associated account as well

    return Response(status=status.HTTP_204_NO_CONTENT)