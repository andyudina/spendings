"""
Rest API to display aggregated spendings
"""
from collections import namedtuple

from rest_framework import (
    serializers, 
    generics, permissions)

from apps.bills.models import Bill
from apps.users.permissions import IsBillOwner
from .models import Spending


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
    """
    spendings = AggregatedByNameSpendingSerializer(
        many=True)
    total = TotalSpendingsSerializer()


class ListAggregatedByNameSpendings(
        generics.GenericAPIView):
    """
    List aggregated by name spendings in given timeframe
    """
    serializer_class = AggregatedSpendingsInTimeFrame
    permission_classes = (
        permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        from rest_framework.response import Response     
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_queryset(self):
        # TODO: validate begin_time and end_time
        AggregatedSpendings = namedtuple(
            'AggregatedSpendings',
            ['spendings', 'total'])
        return AggregatedSpendings(
            spendings=Spending.objects.get_spendings_in_time_frame(
                self.request.user,
                begin_time=self.request.GET.get('begin_time', None),
                end_time=self.request.GET.get('end_time', None)),
            total=Spending.objects.get_total_spendings_in_time_frame(
                self.request.user,
                begin_time=self.request.GET.get('begin_time', None),
                end_time=self.request.GET.get('end_time', None)))


class ItemSerializer(
        serializers.Serializer):
    """
    Validate individual spending
    """
    item = serializers.CharField(
        required=True)
    amount = serializers.FloatField(
        required=True)
    quantity = serializers.IntegerField(
        required=True)


class RewriteSpendingsSerializer(
        serializers.Serializer):
    """
    Validate bill data and rewrite spendings
    """
    bill = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Bill.objects.all())
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

    def save(self):
        Spending.objects.rewrite_spendings_for_bill(
            self.validated_data['bill'],
            self.validated_data['date'],
            self.validated_data['items'])
 

class RewriteSpending(
        generics.CreateAPIView):
    """
    Rewrite spendings related to bill
    With spendings defined by customer

    Warning: preious spendings will be deleted
    """
    serializer_class = RewriteSpendingsSerializer
    permission_classes = (
        permissions.IsAuthenticated, 
        IsBillOwner)

