from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, ProgramViewSet, YearViewSet, 
    SectionViewSet, OrganizationViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'years', YearViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'organizations', OrganizationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
