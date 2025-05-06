from django.urls import path
from .view.auth import admin_login
from .view.admin import insert_admin, get_admin, update_admin, delete_admin
from .view.department import insert_department, get_department, update_department, delete_department
from .view.program import insert_program, get_programs, update_program, delete_program

urlpatterns = [
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/insert/', insert_admin, name='insert_admin'),
    path('admin/get/', get_admin, name='get_admin'),
    path('admin/update/<int:admin_id>/', update_admin, name='update_admin'),
    path('admin/delete/<int:admin_id>/', delete_admin, name='delete_admin'),
    path('department/insert/', insert_department, name='insert_department'),
    path('department/get/', get_department, name='get_department'),
    path('department/update/<int:department_id>/', update_department, name='update_department'),
    path('department/delete/<int:department_id>/', delete_department, name='delete_department'),
    path('program/insert/', insert_program, name='insert_program'),
    path('program/get/', get_programs, name='get_programs'),
    path('program/update/<int:program_id>/', update_program, name='update_program'),
    path('program/delete/<int:program_id>/', delete_program, name='delete_program'),
]
