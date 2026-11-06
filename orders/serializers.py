from rest_framework import serializers

# --- RESPONSE SERIALIZERS ---
class OrderItemResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    productId = serializers.IntegerField(source='product_id')
    productName = serializers.CharField(source='product.name', default='')
    quantity = serializers.IntegerField()
    unitPrice = serializers.DecimalField(source='product.price', max_digits=18, decimal_places=2)

class OrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    userId = serializers.IntegerField(source='user_id')
    createdAt = serializers.DateTimeField(source='created_at')
    totalPrice = serializers.DecimalField(source='total_price', max_digits=18, decimal_places=2)
    status = serializers.SerializerMethodField()
    items = OrderItemResponseSerializer(source='order_items', many=True)

    def get_status(self, obj):
        status_val = obj.status
        mapping = {
            'PENDING': 0, 'PROCESSING': 1, 'SHIPPED': 2, 'DELIVERED': 3, 'CANCELLED': 4,
            'Pending': 0, 'Processing': 1, 'Shipped': 2, 'Delivered': 3, 'Cancelled': 4
        }
        if isinstance(status_val, str):
            return mapping.get(status_val, 0)
        return int(status_val) if status_val is not None else 0

# --- REQUEST SERIALIZERS ---
class CreateOrderItemSerializer(serializers.Serializer):
    productId = serializers.IntegerField(required=False)
    ProductId = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False)
    Quantity = serializers.IntegerField(required=False)

class CreateOrderSerializer(serializers.Serializer):
    items = CreateOrderItemSerializer(many=True, required=False)
    Items = CreateOrderItemSerializer(many=True, required=False)

    def validate(self, attrs):
        items = attrs.get('Items') or attrs.get('items', [])
        normalized_items = []
        for item in items:
            p_id = item.get('ProductId') if item.get('ProductId') is not None else item.get('productId')
            qty = item.get('Quantity') if item.get('Quantity') is not None else item.get('quantity')
            if p_id is not None and qty is not None:
                normalized_items.append({'ProductId': p_id, 'Quantity': qty})
        
        if not normalized_items:
            raise serializers.ValidationError({"Items": ["This field is required."]})
        
        attrs['Items'] = normalized_items
        return attrs

class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    Status = serializers.IntegerField(required=False)

    def validate(self, attrs):
        val = attrs.get('Status') if attrs.get('Status') is not None else attrs.get('status')
        if val is None:
            raise serializers.ValidationError({"Status": ["This field is required."]})
        attrs['Status'] = val
        return attrs