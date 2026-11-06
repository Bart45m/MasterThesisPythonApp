from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ProductResponseSerializer, ProductCreateSerializer
from .logic import ProductService

# KLASA 1: Odpowiada za GET
class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        search = request.query_params.get('search')
        min_price = request.query_params.get('minPrice')
        max_price = request.query_params.get('maxPrice')
        in_stock_param = request.query_params.get('inStock')

        try:
            min_price = float(min_price) if min_price is not None else None
        except ValueError:
            min_price = None

        try:
            max_price = float(max_price) if max_price is not None else None
        except ValueError:
            max_price = None

        in_stock = None
        if in_stock_param is not None:
            in_stock = in_stock_param.lower() in ['true', '1', 'yes']

        products = ProductService.get_products(search, min_price, max_price, in_stock)
        serializer = ProductResponseSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# KLASA 2: Odpowiada za POST
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        role = getattr(request.user, 'role', '')
        
        if not role and request.auth:
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                if isinstance(request.auth, bytes):
                    token_obj = AccessToken(request.auth.decode('utf-8'))
                else:
                    token_obj = AccessToken(str(request.auth))
                role = token_obj.get('role', '')
            except Exception:
                pass

        if role not in ['ADMIN', 'MANAGER']:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product = ProductService.create_product(serializer.validated_data)
        response_serializer = ProductResponseSerializer(product)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)