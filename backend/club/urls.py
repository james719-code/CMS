from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, CustomLoginView, CustomTokenRefreshView,
    AccountViewSet, DepartmentViewSet, ProgramViewSet,
    OrganizationViewSet, MembershipViewSet, MembershipRequestViewSet,
    EventViewSet, EventRegistrationViewSet, AttendanceViewSet, ActivityCategoryViewSet,
    AnnouncementViewSet, NotificationViewSet, BudgetViewSet, BudgetCategoryViewSet,
    FeeViewSet, FeeAssignmentViewSet, PaymentViewSet,
    DocumentViewSet, DocumentCategoryViewSet,
    admin_dashboard_stats, officer_dashboard_stats, organization_report
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'membership-requests', MembershipRequestViewSet)
router.register(r'events', EventViewSet)
router.register(r'event-registrations', EventRegistrationViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'activity-categories', ActivityCategoryViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'budget-categories', BudgetCategoryViewSet)
router.register(r'fees', FeeViewSet)
router.register(r'fee-assignments', FeeAssignmentViewSet)
router.register(r'payments', PaymentViewSet)
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
    path('statistics/organization/<int:org_id>/report/', organization_report, name='organization-report'),
    
    # Router URLs
    path('', include(router.urls)),
]
