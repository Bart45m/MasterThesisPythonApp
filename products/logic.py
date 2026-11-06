import os
from django.conf import settings
from django.db.models import Q
from .models import Product

class ProductService:

    @staticmethod
    def get_products(search=None, min_price=None, max_price=None, in_stock=None):
        products = Product.objects.all()

        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        if min_price is not None:
            products = products.filter(price__gte=min_price)

        if max_price is not None:
            products = products.filter(price__lte=max_price)

        if in_stock is not None and in_stock:
            products = products.filter(quantity__gt=0)

        return products

    @staticmethod
    def create_product(validated_data):
        file_obj = validated_data.get('File')
        file_path = None

        if file_obj:
            try:
                uploads_folder = os.path.join(settings.BASE_DIR, 'wwwroot', 'uploads')
                os.makedirs(uploads_folder, exist_ok=True)

                file_name = file_obj.name
                full_path = os.path.join(uploads_folder, file_name)
                file_path = os.path.join('uploads', file_name).replace('\\', '/')

                with open(full_path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
            except Exception as ex:
                print(f"File save error: {ex}")

        product = Product.objects.create(
            name=validated_data['Name'],
            description=validated_data.get('Description', ''),
            price=validated_data['Price'],
            quantity=validated_data.get('Quantity', 0),
            file_path=file_path,
            is_hidden=False
        )

        return product