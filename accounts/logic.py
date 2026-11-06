import base64
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users

class AuthLogic:

    @staticmethod
    def register_user(validated_data):
        email = validated_data['email']
        if Users.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists.")
        
        hashed = make_password(validated_data['password'])
        user = Users.objects.create(
            email=email,
            password_hash=hashed,
            role='USER'
        )
        return user

    @staticmethod
    def authenticate_user(email, password):
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return None
        
        if not check_password(password, user.password_hash):
            return None
            
        refresh = RefreshToken()
        # Wstrzykujemy customowe claims do tokena JWT
        refresh['user_id'] = user.id
        refresh['email'] = user.email
        refresh['role'] = user.role
        
        return {
            "token": str(refresh.access_token),
            "email": user.email,
            "role": user.role
        }

    @staticmethod
    def generate_reset_token(email):
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return None
        
        # Prosty token bazujący na base64 (dla celów eksperymentu)
        raw_token = f"{user.id}:{user.email}"
        token = base64.b64encode(raw_token.encode()).decode()
        user.reset_token = token
        user.save()
        return token

    @staticmethod
    def reset_password(email, token, new_password):
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return False
            
        if user.reset_token != token:
            return False
            
        user.password_hash = make_password(new_password)
        user.reset_token = None
        user.save()
        return True