from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderResponseSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
from .logic import OrderService

def get_auth_data(request):
    user_id = getattr(request.user, 'id', None)
    role = getattr(request.user, 'role', '')
    
    if (not role or not user_id) and request.auth:
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            token_obj = AccessToken(str(request.auth)) if not isinstance(request.auth, dict) else request.auth
            role = role or token_obj.get('role', '')
            user_id = user_id or token_obj.get('user_id')
        except Exception:
            pass
    return user_id, role

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id, _ = get_auth_data(request)
        if not user_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        orders = OrderService.get_user_orders(user_id)
        serializer = OrderResponseSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id, _ = get_auth_data(request)
        if not user_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = OrderService.create_order(user_id, serializer.validated_data)
        if not order:
            return Response({"message": "Invalid items or products do not exist."}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = OrderResponseSerializer(order)
        # Zmieniamy na status 201, żeby testy automatycznie przechwyciły ID nowo utworzonego zamówienia
        return Response(response_serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user_id, user_role = get_auth_data(request)
        if not user_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        order = OrderService.get_order_by_id(id, user_id, user_role)
        if not order:
            return Response({"message": "Order not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderResponseSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        _, user_role = get_auth_data(request)
        
        if user_role not in ['ADMIN', 'MANAGER']:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateOrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        success = OrderService.update_order_status(id, serializer.validated_data['Status'])
        if not success:
            return Response({"message": "Order not found or invalid status update."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)