"""
Rest API to display aggregated spendings
"""
from rest_framework import (
    serializers, 
    generics)

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
