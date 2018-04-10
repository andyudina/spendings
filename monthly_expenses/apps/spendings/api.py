"""
Rest API to display aggregated spendings
"""
from rest_framework import (
    serializers, 
    generics)

from apps.bills.models import Bill
from .models import Spending


class AggregatedByNameSpendingSerializer(
        serializers.Serializer):
    """
    Read only serializer for aggregated by name spedings
    """
    name = serializers.CharField()
    bills_number = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    total_amount = serializers.FloatField()



class ListAggregatedByNameSpendings(
        generics.ListAPIView):
    """
    List aggregated by name spendings in given timeframe
    """
    # TODO: add authorization
    serializer_class = AggregatedByNameSpendingSerializer

    def get_queryset(self):
        # TODO: validate begin_time and end_time 
        return Spending.objects.get_spendings_in_time_frame(
            begin_time=self.request.GET.get('begin_time', None),
            end_time=self.request.GET.get('end_time', None))


class ItemSerializer(
        serializers.Serializer):
    """
    Validate individual spending
    """
    item = serializers.CharField()
    amount = serializers.FloatField()
    quantity = serializers.IntegerField()


class RewriteSpendingsSerializer(
        serializers.Serializer):
    """
    Validate bill data and rewrite spendings
    """
    bill = serializers.PrimaryKeyRelatedField(
        queryset=Bill.objects.all())
    date = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S')
    items = ItemSerializer(many=True)

    def create(self, validated_data):
        Spending.objects.rewrite_spendings_for_bill(
            validated_data['bill'],
            validated_data['date'],
            validated_data['items'])
 

class RewriteSpending(
        generics.CreateAPIView):
    """
    Rewrite spendings related to bill
    With spendings defined by customer

    Warning: preious spendings will be deleted
    """
    # TODO: add authorization
    serializer_class = RewriteSpendingsSerializer
