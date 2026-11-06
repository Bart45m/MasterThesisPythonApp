from django.db import models
from accounts.models import Users
from products.models import Product

class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    rating = models.IntegerField()
    comment = models.TextField(default='')
    attachment_url = models.CharField(max_length=512, blank=True, null=True, db_column='attachment_url')

    class Meta:
        managed = True
        db_table = 'reviews'