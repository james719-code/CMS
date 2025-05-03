from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Department, Log_Record, Account, Program, Year, Section, Organization, Activity

def insert_department(request):
    # Try to fetch the user, and create it if it doesn't exist
    user, created = User.objects.get_or_create(username='admin', defaults={'password': 'password123'})
    
    if created:
        # If the user was created, ensure we set the password correctly (by default it's not hashed)
        user.set_password('password123')
        user.save()

    # Create and save the new event
    new_department = Department.objects.create(
        name="Computer Science",
        description="Department of Computer Science",
        initials="CS"
    )

    return HttpResponse(f"New Event created: {new_department.name}")

def departments_list(request):
    # Fetch all events from the database
    departments = Department.objects.all()
    
    # Serialize events into a list of dictionaries
    departments_data = []
    for department in departments:
        department_info = {
            'id': department.id,
            'name': department.name,
            'description': department.description,
            'initials': department.initials
        }
        departments_data.append(department_info)

    # Return the events data as JSON
    return JsonResponse(departments_data, safe=False)
