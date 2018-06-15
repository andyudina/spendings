"""
REST API endpoints to parse and upload bills images
"""
import logging

from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from rest_framework import (
    status, serializers, 
    generics, response, permissions)

from apps.budgets.models import Category, BillCategory
from apps.users.permissions import IsBillOwner
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

    @transaction.atomic
    def save_or_get_existing(self):
        """
        Try save serializer or return bill
        if same image was already uploaded
        Returns flag, that shows if bill was created
        and bill
        """
        # TODO: move to the Bill model
        try:
            with transaction.atomic():
                return (
                    True, self.save())
        except IntegrityError as e:
            logger.debug(
                'Can not create new bill '
                'Original error: %s' % str(e))
            sha256_hash_hex = generate_hash_from_image(
                self.validated_data['image'])
            return (
                False, 
                Bill.objects.get(sha256_hash_hex=sha256_hash_hex))


class UploadUniqueBillAPI(
        generics.GenericAPIView):
    """
    Upload bill if not exist
    If exists, returns bill id of exisiting bill

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
        is_created, bill = serializer.save_or_get_existing()
        response_data = {
            'bill': bill.id
        }
        result_status = status.HTTP_201_CREATED if is_created \
            else status.HTTP_200_OK
        return response.Response(
            response_data,
            status=result_status)


## API endpoint to retrieve bill


class CategorySerialiser(
        serializers.ModelSerializer):
    """
    Serialiser for budgeting category
    Read only
    """
    class Meta:
        model = Category
        fields = ('name', )


class BillCategorySerializer(
        serializers.ModelSerializer):
    """
    Serialiser for category of a bill
    """
    category = CategorySerialiser(read_only=True)

    class Meta:
        model = BillCategory
        fields = (
            'id', 'category', 'amount')


class RetrieveBillSerializer(
        serializers.ModelSerializer):
    """
    Serialiser for bill retrieval
    """
    categories = BillCategorySerializer(
        source='bill_to_category',
        many=True, read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        # Remove standart drf behaviour of generating
        # Full urls
        return obj.image.url

    class Meta:
        model = Bill
        fields = (
            'image', 'date', 'categories')

class RetrieveBillAPI(
        generics.RetrieveAPIView):
    """
    Retrieve bill by id

    Successfull response:
        - status code: 200
        - format: {
            'image': [path to image],
            'date': [uploaded date],
            'categories': [
                {
                    id: [category to bill link id],
                    category: {
                        'id': [category id],
                        'name': [category name],
                    },
                    amount: [bill amount for specific category]
                },
            ]
        }
    """
    lookup_url_kwarg = 'bill_id'
    queryset = Bill.objects.all()
    serializer_class = RetrieveBillSerializer
    permission_classes = (
        permissions.IsAuthenticated, 
        IsBillOwner)
