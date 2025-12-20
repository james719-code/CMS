from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Department, Program, Year, Section, Organization, Item, Activity

class DepartmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department_data = {'name': 'Computer Science', 'initials': 'CS', 'description': 'CS Dept'}
        self.department = Department.objects.create(**self.department_data)

    def test_get_departments(self):
        response = self.client.get('/api/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_department(self):
        new_department = {'name': 'Engineering', 'initials': 'ENG', 'description': 'Eng Dept'}
        response = self.client.post('/api/departments/', new_department)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

class ItemTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='CS', initials='CS', description='CS')
        self.program = Program.objects.create(name='CS Program', description='Desc', department=self.department)
        self.organization = Organization.objects.create(name='Coding Club', description='Desc', program=self.program)
        self.activity = Activity.objects.create(name='Hackathon', description='Desc', organization=self.organization)

    def test_create_item_with_integer_quantity(self):
        item = Item.objects.create(
            name='Laptop', 
            description='Dell XPS', 
            quantity=10, 
            price=1000.00, 
            activity=self.activity
        )
        self.assertEqual(item.quantity, 10)
        self.assertIsInstance(item.quantity, int)
