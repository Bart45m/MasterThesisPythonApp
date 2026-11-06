from django.urls import path
from .views import AdminUsersView, AdminUserRoleUpdateView, AdminStatsView, AdminStatsPdfView

urlpatterns = [
    path('users', AdminUsersView.as_view(), name='admin-users'),
    path('users/<int:id>/role', AdminUserRoleUpdateView.as_view(), name='admin-user-role'),
    path('stats', AdminStatsView.as_view(), name='admin-stats'),
    path('stats/pdf', AdminStatsPdfView.as_view(), name='admin-stats-pdf'),
]