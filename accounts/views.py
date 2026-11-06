from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    ForgotPasswordSerializer, 
    ResetPasswordSerializer
)
from .logic import AuthLogic
from .models import Users  # <-- TUTAJ IMPORT MODELU USERS

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            AuthLogic.register_user(serializer.validated_data)
            return Response({"message": "Zarejestrowano pomyślnie"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        result = AuthLogic.authenticate_user(
            serializer.validated_data['email'], 
            serializer.validated_data['password']
        )
        if not result:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
            
        return Response(result, status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.auth.get('user_id')
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "id": user.id,
            "email": user.email,
            "role": user.role
        }, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        token = AuthLogic.generate_reset_token(serializer.validated_data['email'])
        if not token:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({"resetToken": token}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        data = request.data.copy()
        if 'newPassword' in data and 'new_password' not in data:
            data['new_password'] = data['newPassword']
            
        serializer = ResetPasswordSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Pobieramy pole z uwzględnieniem mapowania source='newPassword' w serializatorze
        new_pass = serializer.validated_data.get('newPassword') or serializer.validated_data.get('new_password')
        
        success = AuthLogic.reset_password(
            serializer.validated_data['email'],
            serializer.validated_data['token'],
            new_pass
        )
        if not success:
            return Response({"message": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)