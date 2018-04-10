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
            'parsed_spendings': {
                'date': '%Y-%m-%d 00:00:00',
                'items': [
                    {
                        'item': [item name str],
                        'quantity': [item quantity int],
                        'amount': [item amount float]
                    }
                ]
            }
        }

    Bill can not be parsed:
        - status code: 406
        - format: {
            'bill_id': [bill_id int],
            'parsed_spendings': {
                'error': [parsing error str]
            }
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
            'bill': bill.id}
        try:
            # try parse bill and return parsed info
            response_data['parsed_spendings'] = bill.parse_bill()
        except ValueError as e:
            logger.debug(
                'Can not parse spendins in bill %d' % bill.id)
            # Return parsing error if bill can not be parsed
            response_data['parsed_spendings'] = {
                'error': e.args[0]}
            return response.Response(
                response_data,
                status=status.HTTP_406_NOT_ACCEPTABLE)
        return response.Response(
            response_data,
            status=status.HTTP_201_CREATED)
