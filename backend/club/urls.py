from django.urls import path
from .view.auth import admin_login
from .view.admin import insert_admin, get_admin, update_admin, delete_admin
from .view.department import insert_department, get_department, update_department, delete_department
from .view.program import insert_program, get_programs, update_program, delete_program
from .view.year import insert_year, get_years, update_year, delete_year
from .view.section import insert_section, get_sections, update_section, delete_section
from .view.organization import insert_organization, get_organizations, update_organization, delete_organization

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
    path('year/insert/', insert_year, name='insert_year'),
    path('year/get/', get_years, name='get_years'),
    path('year/update/<int:year_id>/', update_year, name='update_year'),
    path('year/delete/<int:year_id>/', delete_year, name='delete_year'),
    path('section/insert/', insert_section, name='insert_section'),
    path('section/get/', get_sections, name='get_sections'),
    path('section/update/<int:section_id>/', update_section, name='update_section'),
    path('section/delete/<int:section_id>/', delete_section, name='delete_section'),
    path('organization/insert/', insert_organization, name='insert_organization'),
    path('organization/get/', get_organizations, name='get_organizations'),
    path('organization/update/<int:organization_id>/', update_organization, name='update_organization'),
    path('organization/delete/<int:organization_id>/', delete_organization, name='delete_organization'),
]
