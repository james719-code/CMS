# serializers.py
from rest_framework import serializers
from .models import (
    Account, Admin, Department, Program, Year, Section, Organization,
    Member, Officer, Activity, Attendance, Item, Merchandise, File
)

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'password', 'name', 'birthday', 'gender']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class SimpleAccountSerializer(serializers.ModelSerializer):
    """Serializer for nested representations to avoid exposing sensitive data"""
    class Meta:
        model = Account
        fields = ['id', 'username', 'name', 'email']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'initials']

class ProgramSerializer(serializers.ModelSerializer):
    department_details = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'description', 'department', 'department_details']

class YearSerializer(serializers.ModelSerializer):
    program_details = ProgramSerializer(source='program', read_only=True)

    class Meta:
        model = Year
        fields = ['id', 'year', 'program', 'program_details']

class SectionSerializer(serializers.ModelSerializer):
    year_details = YearSerializer(source='year', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'year', 'year_details']

class OrganizationSerializer(serializers.ModelSerializer):
    program_details = ProgramSerializer(source='program', read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'program', 'program_details']

class AdminSerializer(serializers.ModelSerializer):
    account_details = SimpleAccountSerializer(source='account', read_only=True)

    class Meta:
        model = Admin
        fields = ['id', 'account', 'account_details', 'work']

class MemberSerializer(serializers.ModelSerializer):
    account_details = SimpleAccountSerializer(source='account', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'account', 'account_details', 'section', 'section_name', 'organization', 'organization_name']

class OfficerSerializer(serializers.ModelSerializer):
    account_details = SimpleAccountSerializer(source='account', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Officer
        fields = ['id', 'account', 'account_details', 'section', 'organization', 'organization_name', 'position']

class ActivitySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Activity
        fields = ['id', 'name', 'description', 'date', 'organization', 'organization_name']

class AttendanceSerializer(serializers.ModelSerializer):
    member_details = MemberSerializer(source='member', read_only=True)
    activity_details = ActivitySerializer(source='activity', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'member', 'member_details', 'activity', 'activity_details', 'status']

class ItemSerializer(serializers.ModelSerializer):
    activity_details = ActivitySerializer(source='activity', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'quantity', 'price', 'activity', 'activity_details']

class MerchandiseSerializer(serializers.ModelSerializer):
    member_details = MemberSerializer(source='member', read_only=True)
    item_details = ItemSerializer(source='item', read_only=True)

    class Meta:
        model = Merchandise
        fields = ['id', 'member', 'member_details', 'item', 'item_details']

class FileSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = File
        fields = ['id', 'name', 'description', 'file_path', 'organization', 'organization_name']
