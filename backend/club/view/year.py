from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Year
from ..serializers import YearSerializer
from ..decorators import admin_required

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@admin_required
def insert_year(request):
    serializer = YearSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_years(request):
    years = Year.objects.all()
    serializer = YearSerializer(years, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@admin_required
def update_year(request, year_id):
    try:
        year = Year.objects.get(pk=year_id)
    except Year.DoesNotExist:
        return Response({'error': 'Year not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = YearSerializer(year, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Year updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@admin_required
def delete_year(request, year_id):
    try:
        year = Year.objects.get(pk=year_id)
    except Year.DoesNotExist:
        return Response({'error': 'Year not found'}, status=status.HTTP_404_NOT_FOUND)

    year.delete()
    return Response({'message': 'Year deleted successfully'})
