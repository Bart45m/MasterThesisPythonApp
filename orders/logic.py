from .models import Order, OrderItem
from products.models import Product
from accounts.models import Users

class OrderService:

    @staticmethod
    def create_order(user_id, validated_data):
        items_data = validated_data.get('Items', [])
        if not items_data:
            return None
            
        product_ids = list(set(item['ProductId'] for item in items_data))
        # Pobranie produktów z bazy do słownika
        products = Product.objects.filter(id__in=product_ids).in_bulk()

        # Sprawdzenie, czy wszystkie produkty istnieją (zgodność z .NET)
        if len(products) != len(product_ids):
            return None

        total_price = 0
        order_items_to_create = []

        # Tworzymy zamówienie bez przypisanych elementów, aby uzyskać ID
        user_instance = Users.objects.get(id=user_id)
        
        for item in items_data:
            product = products[item['ProductId']]
            total_price += product.price * item['Quantity']
            order_items_to_create.append({
                'product': product,
                'quantity': item['Quantity']
            })

        order = Order.objects.create(
            user=user_instance,
            total_price=total_price,
            status=0 # Pending
        )

        for oi_data in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                product=oi_data['product'],
                quantity=oi_data['quantity']
            )

        return Order.objects.prefetch_related('order_items__product').get(id=order.id)

    @staticmethod
    def get_user_orders(user_id):
        return Order.objects.filter(user_id=user_id).prefetch_related('order_items__product')

    @staticmethod
    def get_order_by_id(order_id, user_id, user_role):
        order = Order.objects.filter(id=order_id).prefetch_related('order_items__product').first()
        if not order:
            return None

        # BOLA / Baseline: dostęp dla właściciela lub konta ADMIN / MANAGER
        if order.user_id != user_id and user_role not in ["ADMIN", "MANAGER"]:
            return None

        return order

    @staticmethod
    def update_order_status(order_id, new_status):
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return False

        order.status = new_status
        order.save()
        return True