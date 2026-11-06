import os
from django.conf import settings
from .models import Review
from products.models import Product
from accounts.models import Users

class ReviewService:

    @staticmethod
    def get_reviews_by_product(product_id):
        return Review.objects.filter(product_id=product_id).select_related('user')

    @staticmethod
    def create_review(user_id, validated_data):
        product_id = validated_data['productId']
        if not Product.objects.filter(id=product_id).exists():
            return None

        attachment_url = None
        file_obj = validated_data.get('file')

        if file_obj:
            try:
                upload_dir = os.path.join(settings.BASE_DIR, 'wwwroot', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_name = file_obj.name
                full_path = os.path.join(upload_dir, file_name)
                attachment_url = f"uploads/{file_name}"

                with open(full_path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
            except Exception as ex:
                print(f"File save error: {ex}")

        review = Review.objects.create(
            product_id=product_id,
            user_id=user_id,
            rating=validated_data['rating'],
            comment=validated_data.get('comment', ''),
            attachment_url=attachment_url
        )

        return Review.objects.select_related('user').get(id=review.id)

    @staticmethod
    def delete_review(review_id, user_id, user_role):
        review = Review.objects.filter(id=review_id).first()
        if not review:
            return False

        # Weryfikacja: Właściciel opinii LUB Admin / Manager[cite: 15]
        if review.user_id != user_id and user_role not in ["ADMIN", "MANAGER"]:
            return False

        review.delete()
        return True