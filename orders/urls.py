from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import OrderListView, OrderCreateView, OrderDetailView, OrderStatusUpdateView

@csrf_exempt
def order_dispatcher(request, *args, **kwargs):
    if request.method == 'POST':
        return OrderCreateView.as_view()(request, *args, **kwargs)
    return OrderListView.as_view()(request, *args, **kwargs)

urlpatterns = [
    # Główne żądania pod /api/orders (GET i POST)
    path('', order_dispatcher, name='orders-dispatch'),
    
    # Żądania do konkretnego zamówienia /api/orders/{id}
    path('/<int:id>', OrderDetailView.as_view(), name='order-detail'),
    
    # Aktualizacja statusu /api/orders/{id}/status
    path('/<int:id>/status', OrderStatusUpdateView.as_view(), name='order-status-update'),
]