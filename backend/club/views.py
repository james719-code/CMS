from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.models import User
from .view.department import insert_department, get_department, update_department, delete_department
from .view.admin import insert_admin, get_admin, update_admin
