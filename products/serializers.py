from rest_framework import serializers
from .models import Product

class ProductResponseSerializer(serializers.ModelSerializer):
    filePath = serializers.CharField(source='file_path', allow_null=True)
    isHidden = serializers.BooleanField(source='is_hidden')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity', 'filePath', 'isHidden']

class ProductCreateSerializer(serializers.Serializer):
    Name = serializers.CharField(max_length=255)
    Description = serializers.CharField(required=False, allow_blank=True, default='')
    Price = serializers.DecimalField(max_digits=18, decimal_places=2)
    Quantity = serializers.IntegerField(default=0)
    File = serializers.FileField(required=False, allow_null=True)