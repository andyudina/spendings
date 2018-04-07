"""
REST API endpoints to parse and upload bills images
"""
from django.db import transaction
from rest_framework import (
    status, serializers, 
    generics, response)

from .models import Bill
from .utils import generate_hash_from_image


IMAGE_ALREADY_UPLOADED_ERROR = 'This image was already uploaded'


class CreateBillSerializer(
        serializers.ModelSerializer):
    """
    Serialiser for bill creation
    Validates if bill was already uploaded 
    """
    class Meta:
        model = Bill
        fields = ('image', )

    def validate_image(self, image):
        """
        Validate that the image was not uploaded yet
        """
        # WARNING: prone to race conditions here
        sha256_hash_hex = generate_hash_from_image(image)
        if Bill.objects.\
                filter(sha256_hash_hex=sha256_hash_hex).\
                exists():
            raise serializers.ValidationError(
                IMAGE_ALREADY_UPLOADED_ERROR)
        return image


class UploadBillAPI(
        generics.GenericAPIView):
    """
    Upload bill if not exist
    Returns parsed bill info
    """
    serializer_class = CreateBillSerializer
    # TODO: permissions to APIs
    def post(
            self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            bill = serializer.save()
        try:
            data = bill.parse_bill()
        except ValueError as e:
            return response.Response({
                    'error': e.args[0]
                },
                status=status.HTTP_400_BAD_REQUEST)
        return response.Response(
            data,
            status=status.HTTP_201_CREATED)

