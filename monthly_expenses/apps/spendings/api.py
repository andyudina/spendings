"""
Rest API to display aggregated spendings
"""
import logging
from collections import namedtuple

from django.db import transaction
from rest_framework import (
    serializers, 
    response, status,
    generics, permissions)

from apps.bills.models import Bill
from apps.users.permissions import IsOwner
from .models import Spending

logger = logging.getLogger(__name__)


## Spendings aggregation APIS


class DatesSerializer(
        serializers.Serializer):
    """
    Validate that passed dates are in right format
    Accepts None values or valid dates
    """
    begin_time = serializers.DateField(
        required=False)
    end_time = serializers.DateField(
        required=False)


class AggregatedByNameSpendingSerializer(
        serializers.Serializer):
    """
    Read only serializer for aggregated by name spedings
    """
    name = serializers.CharField(required=True)
    bills_number = serializers.IntegerField(required=True)
    total_quantity = serializers.IntegerField(required=True)
    total_amount = serializers.FloatField(required=True)


class TotalSpendingsSerializer(
        serializers.Serializer):
    """
    Read only serializer for total spendings
    """
    total_bills_number = serializers.IntegerField(required=True)
    total_quantity = serializers.IntegerField(required=True)
    total_amount = serializers.FloatField(required=True)


class AggregatedSpendingsInTimeFrame(
        serializers.Serializer):
    """
    Read only serializer for aggregated spendings in time frame
    and their total amounts and quantity
    """
    spendings = AggregatedByNameSpendingSerializer(
        many=True)
    total = TotalSpendingsSerializer()


class BaseSpendingsAggregationView(
        generics.GenericAPIView):
    """
    Base class for displaying spendings aggregation
    """
    permission_classes = (
        permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        from rest_framework.response import Response
        self._validate_dates_format(request.GET)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def _validate_dates_format(self, query):
        """
        Validate if passed dates can be recognized
        """
        dates_serializer = DatesSerializer(data=query)
        dates_serializer.is_valid(
            raise_exception=True)


class ListMostExpensiveSpendings(
        BaseSpendingsAggregationView):
    """
    List aggregated by name spendings in given timeframe
    sorted by total amount
    """
    serializer_class = AggregatedSpendingsInTimeFrame

    def get_queryset(self):
        AggregatedSpendings = namedtuple(
            'AggregatedSpendings',
            ['spendings', 'total'])
        return AggregatedSpendings(
            spendings=Spending.objects.get_expensive_spendings_in_time_frame(
                self.request.user,
                begin_time=self.request.GET.get('begin_time', None),
                end_time=self.request.GET.get('end_time', None)),
            total=Spending.objects.get_total_spendings_in_time_frame(
                self.request.user,
                begin_time=self.request.GET.get('begin_time', None),
                end_time=self.request.GET.get('end_time', None)))


class AggregatedSpendingsWithoutTotal(
        serializers.Serializer):
    """
    Read only serializer for aggregated spendings in time frame
    """
    spendings = AggregatedByNameSpendingSerializer(
        many=True)


class ListMostPopularSpendings(
        BaseSpendingsAggregationView):
    """
    List aggregated by name spendings in given timeframe
    sorted by total quantity
    """
    serializer_class = AggregatedSpendingsWithoutTotal

    def get_queryset(self):
        AggregatedSpendings = namedtuple(
            'AggregatedSpendings', ['spendings',])
        return AggregatedSpendings(
            spendings=Spending.objects.get_popular_spendings_in_time_frame(
                self.request.user,
                begin_time=self.request.GET.get('begin_time', None),
                end_time=self.request.GET.get('end_time', None)))


## Spendings modification API


class ItemSerializer(
        serializers.ModelSerializer):
    """
    Validate individual spending
    """

    class Meta:
        model = Spending
        fields = (
            'name', 'amount', 'quantity')


class RewriteSpendingsSerializer(
        serializers.Serializer):
    """
    Validate bill data and rewrite spendings
    """
    date = serializers.DateTimeField(
        required=True,
        format='%Y-%m-%d %H:%M:%S')
    items = ItemSerializer(
        required=True,
        many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                'Items can not be blank')
        return items

    @transaction.atomic
    def save_spendings_for_bill(self, bill):
        """
        Create spendings passed to serializer
        Link them to bill
        Delete previous bill spendings

        Update purchase date for bill
        """
        Spending.objects.rewrite_spendings_for_bill(
            bill,
            self.validated_data['date'],
            self.validated_data['items'])
        bill.date = self.validated_data['date']
        bill.save(update_fields=['date'])


class ListSpendingsSerializer(
        serializers.Serializer):
    """
    Read only serilaizer to list spendings for the bill
    """
    # bill purchase date
    date = serializers.DateField(
        required=False,
        format='%Y-%m-%d')
    items = ItemSerializer(
        required=True,
        many=True)


class ListOrRewriteSpending(
        generics.GenericAPIView):
    """
    POST: Rewrite spendings related to bill
    With spendings defined by customer

    Accepts spendings in format: 
    {
      'date': [spendings created date: %Y-%m-%d 00:00:00],
      'items': [
        {
          'name': [item name: str],
          'amount': [amount: int],
          'quantity': [quantity: float]
        }
      ]
    }

    Warning: preious spendings will be deleted

    GET: return parsed and saved list of spendings related to bill.
    returns spendings in format: 
    {
      'spendings_saved': {
        #spendings that are saved to database
        'items': [
          {
            'name': [item name: str],
            'amount': [amount: int],
            'quantity': [quantity: float]
          }
          'date': [spendings created date: %Y-%m-%d 00:00:00],'
        ],
       },
      'spendings_parsed': {
        'parse_error': [error during parsing or None],
        'date': [spendings created date: %Y-%m-%d 00:00:00],
        'items': [
          {
            'name': [item name: str],
            'amount': [amount: int],
            'quantity': [quantity: float]
          }
        ]
      }
    }
    """
    queryset = Bill.objects.all()
    lookup_url_kwarg = 'bill_id'
    permission_classes = (
        permissions.IsAuthenticated, 
        IsOwner)

    def get_serializer_class(self):
        """
        Used only for displaying drf docs
        """
        if self.request.method == 'GET':
            return ListSpendingsSerializer
        elif self.request.method == 'POST':
            return RewriteSpendingsSerializer

    def get(self, *args, **kwargs):
        bill = self.get_object()
        spendings_serializer = ListSpendingsSerializer(
            {
                'date': bill.date, 
                'items': bill.spendings
            })
        result = {
            'spendings_saved': spendings_serializer.data
        }
        # populate result with parsed spendings
        result['spendings_parsed'] = self._get_parsed_spendings(bill)
        return response.Response(
            result, 
            status=status.HTTP_200_OK)

    def _get_parsed_spendings(self, bill):
        """
        Try get parsed spendings from bill
        return data in format:
        {
          'parse_error': [error during parsing or None],
          'date': [spendings created date: %Y-%m-%d 00:00:00],
          'items': [
            {
              'name': [item name: str],
              'amount': [amount: int],
              'quantity': [quantity: float]
            }
          ]
        }
        """
        try:
            spendings = bill.parse_bill()
            spendings['parse_error'] = None
            return spendings
        except ValueError as e:
            logger.debug(
                'Can not parse spendins in bill %d' % bill.id)
            # Return parsing error if bill can not be parsed
            return {
                'parse_error': e.args[0],
                'date': None,
                'items': []
            }

    def post(self, request, *args, **kwargs):
        bill = self.get_object()
        serializer = RewriteSpendingsSerializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save_spendings_for_bill(bill)
        return response.Response(
            serializer.data, 
            status=status.HTTP_200_OK)
