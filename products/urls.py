from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import ProductListView, ProductCreateView

@csrf_exempt
def product_dispatcher(request, *args, **kwargs):
    # Sprawdzamy metodę z testu i kierujemy do odpowiedniej z Twoich klas
    if request.method == 'POST':
        return ProductCreateView.as_view()(request, *args, **kwargs)
    return ProductListView.as_view()(request, *args, **kwargs)

urlpatterns = [
    # Rejestrujemy rozdzielacz pod pustą ścieżką
    path('', product_dispatcher, name='products-dispatch'),
]