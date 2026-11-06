from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.renderers import BaseRenderer
from django.http import HttpResponse
from datetime import datetime
from .serializers import UserResponseSerializer, UpdateUserRoleSerializer, DashboardStatsResponseSerializer
from .logic import AdminService

class BinaryRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', '')
        return role == 'ADMIN'

class IsAdminOrManagerRole(BasePermission):
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', '')
        return role in ['ADMIN', 'MANAGER']

class AdminUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManagerRole]

    def get(self, request):
        users = AdminService.get_all_users()
        serializer = UserResponseSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminUserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, id):
        serializer = UpdateUserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success = AdminService.update_user_role(id, serializer.validated_data['role'])
        if not success:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "User role updated successfully."}, status=status.HTTP_200_OK)

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManagerRole]

    def get(self, request):
        stats = AdminService.get_dashboard_stats()
        serializer = DashboardStatsResponseSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminStatsPdfView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManagerRole]
    renderer_classes = [BinaryRenderer]

    def get(self, request):
        pdf_bytes = AdminService.generate_pdf_report()
        file_name = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response