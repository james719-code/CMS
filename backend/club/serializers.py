from rest_framework import serializers
from .models import Department, Member, Class, Officer, Program, Organization, Event

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
