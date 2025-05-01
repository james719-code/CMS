from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .models import Event
from django.utils import timezone
from django.contrib.auth.models import User

def insert_event(request):
    # Try to fetch the user, and create it if it doesn't exist
    user, created = User.objects.get_or_create(username='admin', defaults={'password': 'password123'})
    
    if created:
        # If the user was created, ensure we set the password correctly (by default it's not hashed)
        user.set_password('password123')
        user.save()

    # Create and save the new event
    new_event = Event.objects.create(
        name="Club Orientation",
        description="Introductory meeting for new members",
        date=timezone.datetime(2025, 5, 10, 10, 0),
        location="Main Hall",
        created_by=user
    )

    return HttpResponse(f"New Event created: {new_event.name}")

def events_list(request):
    # Fetch all events from the database
    events = Event.objects.all()
    
    # Serialize events into a list of dictionaries
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "date": event.date.strftime('%Y-%m-%d %H:%M:%S'),
            "location": event.location,
            "created_by": event.created_by.username
        })
    
    # Return the events data as JSON
    return JsonResponse(events_data, safe=False)
