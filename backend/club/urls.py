from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, CustomLoginView, CustomTokenRefreshView,
    AccountViewSet, DepartmentViewSet, ProgramViewSet,
    OrganizationViewSet, MembershipViewSet, MembershipRequestViewSet,
    EventViewSet, AttendanceViewSet, ActivityCategoryViewSet,
    AnnouncementViewSet, BudgetViewSet, BudgetCategoryViewSet,
    DocumentViewSet, DocumentCategoryViewSet,
    admin_dashboard_stats, officer_dashboard_stats
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'membership-requests', MembershipRequestViewSet)
router.register(r'events', EventViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'activity-categories', ActivityCategoryViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'budget-categories', BudgetCategoryViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'document-categories', DocumentCategoryViewSet)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Dashboard Statistics
    path('statistics/admin/', admin_dashboard_stats, name='admin-dashboard-stats'),
    path('statistics/officer/<int:org_id>/', officer_dashboard_stats, name='officer-dashboard-stats'),
    
    # Router URLs
    path('', include(router.urls)),
]
