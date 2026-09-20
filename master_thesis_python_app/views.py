import os
import hashlib
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Importy potrzebne do automatycznego wygenerowania pól parametrów w Swaggerze
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

# ==============================================================================
# 0. KLASA BAZOWA (Wspólne dziedziczenie sekretów dla celów SAST)
# ==============================================================================
class BaseVulnerableAPIView(APIView):
    # PODATNOŚĆ 1: Hardcoded Secret (Twardo zakodowane klucze/hasła)
    ADMIN_API_KEY = "AIzaSyD-TEST-KEY-99283112-Xyz7788A"
    CONNECTION_STRING = "Server=myServerAddress;Database=myDataBase;User Id=admin;Password=SuperSecretPassword123!;"


# ==============================================================================
# 1. SQL INJECTION (Podatność na wstrzykiwanie kodu SQL)
# ==============================================================================
class SqlInjectionAPIView(BaseVulnerableAPIView):
    """
    1. SQL INJECTION (Podatność na wstrzykiwanie kodu SQL)
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='searchTerm', 
                type=OpenApiTypes.STR, 
                location=OpenApiParameter.QUERY, 
                required=True, 
                description="Fraza wyszukiwania (odpowiednik [FromQuery] string searchTerm)"
            )
        ]
    )
    def get(self, request):
        search_term = request.query_params.get('searchTerm', '')

        # BŁĄD SAST: Bezpośrednie łączenie stringów (String Concatenation) zamiast użycia parametrów.
        query = f"SELECT * FROM Users WHERE UserName = '{search_term}'"

        with connection.cursor() as cursor:
            # Identyczna odpowiedź jak w .NET: return Ok(new { Message = ... })
            return Response({"Message": f"Wykonano podatne zapytanie: {query}"}, status=status.HTTP_200_OK)


# ==============================================================================
# 2. PATH TRAVERSAL / ARBITRARY FILE READ (Nieautoryzowany dostęp do plików)
# ==============================================================================
class PathTraversalAPIView(BaseVulnerableAPIView):
    """
    2. PATH TRAVERSAL / ARBITRARY FILE READ (Nieautoryzowany dostęp do plików systemowych)
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='fileName', 
                type=OpenApiTypes.STR, 
                location=OpenApiParameter.QUERY, 
                required=True, 
                description="Nazwa pliku logów (odpowiednik [FromQuery] string fileName)"
            )
        ]
    )
    def get(self, request):
        file_name = request.query_params.get('fileName', '')

        # BŁĄD SAST: Brak walidacji i oczyszczania (sanitization) ścieżki.
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, "Logs", file_name)

        if os.path.exists(full_path):
            # Identyczna odpowiedź jak w .NET: return Ok(new { FilePath = ..., Content = ... })
            return Response({
                "FilePath": full_path, 
                "Content": "Zawartość pliku logów..."
            }, status=status.HTTP_200_OK)

        # Identyczna odpowiedź jak w .NET: return NotFound();
        return Response({"Detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


# ==============================================================================
# 3. WEAK CRYPTOGRAPHY (Użycie słabych algorytmów haszujących)
# ==============================================================================
class WeakCryptographyAPIView(BaseVulnerableAPIView):
    """
    3. WEAK CRYPTOGRAPHY (Użycie słabych algorytmów haszujących)
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='password', 
                type=OpenApiTypes.STR, 
                location=OpenApiParameter.QUERY,  # Wskazanie, że parametr przekazywany jest w URL (?password=...)
                required=True, 
                description="Hasło do zahaszowania (odpowiednik [FromQuery] string password)"
            )
        ]
    )
    def post(self, request):
        # Pobieramy hasło bezpośrednio z adresu URL (query params), tak jak zadeklarowałeś w .NET przez [FromQuery]
        password = request.query_params.get('password', '')

        # BŁĄD SAST: MD5 jest uznawany za złamany i podatny na kolizje.
        md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

        # Identyczna odpowiedź jak w .NET: return Ok(new { PasswordHash = hash });
        return Response({"PasswordHash": md5_hash}, status=status.HTTP_200_OK)
