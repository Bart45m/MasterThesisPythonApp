from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Users
from products.models import Product

class OrderStatus(models.IntegerChoices):
    PENDING = 0
    PROCESSING = 1
    SHIPPED = 2
    DELIVERED = 3
    CANCELLED = 4

class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)

    class Meta:
        managed = True
        db_table = 'orders'

class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'order_items'