from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ReviewResponseSerializer, CreateReviewSerializer
from .logic import ReviewService

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

class ReviewListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, productId):
        reviews = ReviewService.get_reviews_by_product(productId)
        serializer = ReviewResponseSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id, _ = get_auth_data(request)
        if not user_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = CreateReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        review = ReviewService.create_review(user_id, serializer.validated_data)
        if not review:
            return Response({"message": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = ReviewResponseSerializer(review)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

class ReviewDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        user_id, user_role = get_auth_data(request)
        if not user_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        success = ReviewService.delete_review(id, user_id, user_role)
        if not success:
            return Response({"message": "Review not found or permission denied."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Review deleted successfully."}, status=status.HTTP_200_OK)