from django.urls import path
from . import views

urlpatterns = [
    path('api/events/', views.events_list, name='events_list'),
    path('insert_event/', views.insert_event, name='insert-event'),
]
