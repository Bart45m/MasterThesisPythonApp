from django.urls import path
from .views import SqlInjectionAPIView, PathTraversalAPIView, WeakCryptographyAPIView

urlpatterns = [
    # Mapowanie każdej podklasy na dedykowany endpoint URL
    path('search-users/', SqlInjectionAPIView.as_view(), name='search-users'),
    path('read-log/', PathTraversalAPIView.as_view(), name='read-log'),
    path('hash-password/', WeakCryptographyAPIView.as_view(), name='hash-password'),
]
