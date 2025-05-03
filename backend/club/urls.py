from django.urls import path
from . import views

urlpatterns = [
    path('api/departments/', views.departments_list, name='departments_list'),
    path('insert_department/', views.insert_department, name='insert-department'),
]
