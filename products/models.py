from django.db import models

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=18, decimal_places=2)
    quantity = models.IntegerField(default=0)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'products'

    def __str__(self):
        return self.name