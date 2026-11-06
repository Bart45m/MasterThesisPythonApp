from rest_framework import serializers

class ReviewResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    productId = serializers.IntegerField(source='product_id')
    userId = serializers.IntegerField(source='user_id')
    userEmail = serializers.CharField(source='user.email', default='')
    rating = serializers.IntegerField()
    comment = serializers.CharField()
    attachmentUrl = serializers.CharField(source='attachment_url', allow_null=True, default='')

class CreateReviewSerializer(serializers.Serializer):
    productId = serializers.IntegerField(required=False)
    ProductId = serializers.IntegerField(required=False)
    rating = serializers.IntegerField(required=False)
    Rating = serializers.IntegerField(required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    Comment = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True)
    File = serializers.FileField(required=False, allow_null=True)

    def validate(self, attrs):
        # Obsługa wielkich i małych liter wysyłanych w formularzu multipart/form-data
        p_id = attrs.get('ProductId') if attrs.get('ProductId') is not None else attrs.get('productId')
        rating = attrs.get('Rating') if attrs.get('Rating') is not None else attrs.get('rating')
        comment = attrs.get('Comment') if attrs.get('Comment') is not None else attrs.get('comment', '')
        file = attrs.get('File') if attrs.get('File') is not None else attrs.get('file')

        if p_id is None or rating is None:
            raise serializers.ValidationError({"detail": "ProductId and Rating are required."})

        attrs['productId'] = p_id
        attrs['rating'] = rating
        attrs['comment'] = comment
        attrs['file'] = file
        return attrs