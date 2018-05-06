"""
REST API endpoints to parse and upload bills images
"""
import logging

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import (
    status, serializers, 
    generics, response, permissions)

from .models import Bill
from .utils import generate_hash_from_image


logger = logging.getLogger(__name__)
IMAGE_ALREADY_UPLOADED_ERROR = 'This image was already uploaded'


class CreateBillSerializer(
        serializers.ModelSerializer):
    """
    Serialiser for bill creation
    Validates if bill was already uploaded 
    """
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )

    class Meta:
        model = Bill
        fields = ('image', 'user')

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
    Returns parsed bill info and bill id.

    Successfull response:
        - status code: 201
        - format: {
            'bill_id': [bill_id int],
        }

    Problems with upload:
        - status code: 400
    """
    serializer_class = CreateBillSerializer
    permission_classes = (
        permissions.IsAuthenticated, )

    def post(
            self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            bill = serializer.save()
        response_data = {
            'bill': bill.id
        }
        return response.Response(
            response_data,
            status=status.HTTP_201_CREATED)
