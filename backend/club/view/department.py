# views/department.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Department
from ..serializers import DepartmentSerializer

@api_view(['POST'])
def insert_department(request):
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_department(request):
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepartmentSerializer(department, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Department updated successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

    department.delete()
    return Response({'message': 'Department deleted successfully'})