from rest_framework import serializers

class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    role = serializers.CharField()

class UpdateUserRoleSerializer(serializers.Serializer):
    role = serializers.IntegerField()

class DashboardStatsResponseSerializer(serializers.Serializer):
    totalUsers = serializers.IntegerField()
    totalProducts = serializers.IntegerField()
    totalOrders = serializers.IntegerField()
    totalRevenue = serializers.CharField()
    ordersByStatus = serializers.DictField()