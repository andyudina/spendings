"""
REST API endpoints to parse and upload bills images
"""
import logging

from django.db import transaction, IntegrityError
from django.db.models import Count
from django.contrib.auth.models import User
from rest_framework import (
    mixins,
    exceptions, status, serializers,
    generics, response, permissions)

from apps.budgets.models import Category, BillCategory
from apps.users.permissions import IsOwner
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


class ListBillsSerialiser(
        serializers.ModelSerializer):
    """
    Serialiser for bill listing
    Shows if bills were categorised
    """
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        # Remove standart drf behaviour of generating
        # Full urls
        return obj.image.url

    class Meta:
        model = Bill
        fields = ('image', 'id', 'has_categories')


class ListUploadUniqueBillAPI(
        mixins.ListModelMixin,
        generics.GenericAPIView):
    """
    POST:
        Upload bill if not exist
        If exists, returns bill id of exisiting bill

        Successfull response:
            - status code: 201
            - format: {
                'bill_id': [bill_id int],
            }

        Problems with upload:
            - status code: 400
    GET:
        List bills for current user
        Successfull response:
            - status code: 200
            - format: [
                {
                   'id': [bill id],
                   'image':, [image url]
                   'has_categories': [true if bill was categorised]
                }
            ]
    """
    permission_classes = (
        permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateBillSerializer
        elif self.request.method == 'GET':
            return ListBillsSerialiser
        raise exceptions.MethodNotAllowed(self.request.method)

    def get_queryset(self):
        """
        On get request this view should return a list of all bills
        for the currently authenticated user.
        """
        user = self.request.user
        qs = Bill.objects.\
            prefetch_related('categories').\
            filter(user=user)
        if self.request.GET.get('uncategorised'):
            # filter out bills
            # with categories
            qs = qs.\
                annotate(categories_number=Count('categories')).\
                filter(categories_number=0)
        return qs

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

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
    id = serializers.IntegerField(
        # need to pass id to update
        read_only=False)
    name = serializers.CharField(read_only=True)

    def validate_id(self, value):
        """
        Make sure that id belongs to existing category
        """
        if Category.objects.\
                filter(id=value).\
                exists() == False:
            raise serializers.ValidationError(
                'Non existing categoru')
        return value

    class Meta:
        model = Category
        fields = ('name', 'id')


class BillCategorySerializer(
        serializers.ModelSerializer):
    """
    Serialiser for category of a bill
    """
    category = CategorySerialiser(read_only=False)

    class Meta:
        model = BillCategory
        fields = (
            'id', 'category', 'amount')


class RetrieveUpdateBillSerializer(
        serializers.ModelSerializer):
    """
    Serialiser for bill retrieval
    """
    categories = BillCategorySerializer(
        read_only=False,
        source='bill_to_category',
        many=True)
    # method field is read only by feafult
    image = serializers.SerializerMethodField()
    date = serializers.DateTimeField(read_only=True)

    def get_image(self, obj):
        # Remove standart drf behaviour of generating
        # Full urls
        return obj.image.url

    @transaction.atomic
    def update(
            self, instance, validated_data):
        """
        Update categories, linked to bill
        Rewrites all the categories by deleting previous categories links
        and creating brand new ones
        """
        instance.categories.clear()
        instance.create_categories_in_bulk(
            validated_data['bill_to_category'])
        return instance

    class Meta:
        model = Bill
        fields = (
            'image', 'date', 'categories')


class RetrieveUpdateBillAPI(
        generics.RetrieveUpdateAPIView):
    """
    Retrieve or updates bill by id

    GET:
    Retrieve bill info and categories
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
    PATCH:
    Used to update bill categories only
    Successfull response:
        - status code: 200
    Errors on update:
        - status code: 400
    """
    lookup_url_kwarg = 'bill_id'
    queryset = Bill.objects.all()
    serializer_class = RetrieveUpdateBillSerializer
    permission_classes = (
        permissions.IsAuthenticated, 
        IsOwner)