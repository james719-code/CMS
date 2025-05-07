# serializers.py
from rest_framework import serializers
from .models import Account, Admin, Department, Program, Year

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'password', 'name', 'birthday', 'gender']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class AdminSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Admin
        fields = ['id', 'account', 'work']

    def create(self, validated_data):
        account_data = validated_data.pop('account')
        account = Account.objects.create(**account_data)
        admin = Admin.objects.create(account=account, **validated_data)
        return admin

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'initials']

class ProgramSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    department_details = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'description', 'department', 'department_details']

class YearSerializer(serializers.ModelSerializer):
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())

    class Meta:
        model = Year
        fields = ['id', 'year', 'program']