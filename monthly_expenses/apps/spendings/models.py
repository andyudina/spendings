# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class SpendingsManager(models.Manager):
    """
    Spendings aggregation logic
    """

    def get_spendings_in_time_frame(
            self, begin_time=None, end_time=None):
        """
        Aggregates spendings by date and item
        Returns sorted list of items with their quanuity and total amount
        in given time frame.time
        End time is not included.
        Returns annotated QuerySet
        """
        qs = self.all()
        if begin_time:
            qs = qs.filter(date__gte=begin_time)
        if end_time:
            qs = qs.filter(date__lt=end_time)
        return qs.values('name').\
               annotate(
                   bills_number = models.Count('bill', distinct=True),
                   total_quantity=models.Sum('quantity'),
                   total_amount=models.Sum(models.F('amount') * models.F('quantity'))).\
               order_by('-total_amount')


class Spending(models.Model):
    """
    Spendings quantity and individual amount by date and item name
    """
    name = models.CharField(
        verbose_name='Bought item name',
        max_length=128, null=False, blank=False)
    quantity = models.IntegerField(
        default=1, null=False, blank=False)
    # we don't need precise numbers here
    amount = models.FloatField(
        verbose_name='Price of one item',
        null=False, blank=False)
    date = models.DateField(
        verbose_name='Date of the spending')
    bill = models.ForeignKey('bills.Bill')
    create_time = models.DateTimeField(
        verbose_name='Speding was logged',
        auto_now_add=True)

    objects = SpendingsManager()

    class Meta:
        unique_together = (
                'name', 'bill') # requires preaggregation of the same items in one bill
