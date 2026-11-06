from django.urls import path
from .views import ReviewListCreateView, ReviewDeleteView

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review-create'),
    path('/product/<int:productId>', ReviewListCreateView.as_view(), name='reviews-by-product'),
    path('/<int:id>', ReviewDeleteView.as_view(), name='review-delete'),
]