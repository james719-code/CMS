from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    DepartmentViewSet, ProgramViewSet, YearViewSet, 
    SectionViewSet, OrganizationViewSet,
    RegisterView, CustomLoginView,
    AdminViewSet, MemberViewSet, OfficerViewSet,
    ActivityViewSet, AttendanceViewSet, ItemViewSet,
    MerchandiseViewSet, FileViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'years', YearViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'admins', AdminViewSet)
router.register(r'members', MemberViewSet)
router.register(r'officers', OfficerViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'items', ItemViewSet)
router.register(r'merchandise', MerchandiseViewSet)
router.register(r'files', FileViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', CustomLoginView.as_view(), name='auth_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
