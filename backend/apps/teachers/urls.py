from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaveRequestViewSet, AdminLeaveViewSet

router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-requests')
router.register(r'admin/leaves', AdminLeaveViewSet, basename='admin-leaves')

urlpatterns = [
    path('', include(router.urls)),
]