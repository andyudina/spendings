# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import models, transaction

from .utils import aggregate_spendings_by_name


logger = logging.getLogger(__name__)


class SpendingsManager(models.Manager):
    """
    Spendings aggregation logic
    """

    def get_expensive_spendings_in_time_frame(
            self, *args, **kwargs):
        """
        Return aggrergated spndings by item in given time frame
        sorted by total amount
        """
        return \
            self.get_spendings_in_time_frame(*args, **kwargs).\
                 order_by('-total_amount')

    def get_popular_spendings_in_time_frame(
            self, *args, **kwargs):
        """
        Return aggrergated spndings by item in given time frame
        sorted by total quantity
        """
        return \
            self.get_spendings_in_time_frame(*args, **kwargs).\
                 order_by('-total_quantity')
   
    def get_spendings_in_time_frame(
            self, user, 
            begin_time=None, end_time=None):
        """
        Aggregates spendings by item
        Returns sorted list of items with their quanuity and total amount
        in given time frame.time
        End time is not included.
        Returns annotated QuerySet.
        """
        qs = self.filter(bill__user=user)
        if begin_time:
            qs = qs.filter(date__gte=begin_time)
        if end_time:
            qs = qs.filter(date__lt=end_time)
        return qs.values('name').\
               annotate(
                   bills_number=models.Count('bill', distinct=True),
                   total_quantity=models.Sum('quantity'),
                   total_amount=models.Sum('amount'))

    def get_total_spendings_in_time_frame(
            self, user,
            begin_time=None, end_time=None):
        """
        Aggregate spendings in a timeframe
        Returns dictionary with format
        {
            'total_bills_number': [total_bills_number int],
            'total_quantity': [total spendings quantity int],
            'total_amunt': [total spendings amount int],
        }
        """
        qs = self.filter(bill__user=user)
        if begin_time:
            qs = qs.filter(date__gte=begin_time)
        if end_time:
            qs = qs.filter(date__lt=end_time)
        result = qs.aggregate(
            total_bills_number=models.Count('bill', distinct=True),
            total_quantity=models.Sum('quantity'),
            total_amount=models.Sum('amount'))
        # return 0 instead of None for aggregated data
        for key in [
                'total_amount',
                'total_bills_number',
                'total_quantity']:
            result[key] = result[key] or 0
        return result

    @transaction.atomic
    def rewrite_spendings_for_bill(
            self, bill, date, spendings):
        """
        Delete all spendings for bill
        and create new one form passed spendings.

        Accept spendings as a list of dics:
        [
            {
                'item': [item name str],
                'quantity': [item quantity int],
                'amount': [total amount for specified quantity float]
            }
        ]
        """
        # delete all previous spendings
        self.filter(
            bill=bill).delete()
        # create new spendings
        items = aggregate_spendings_by_name(
            spendings)
        for name, item in items.items():
            # impossible to get Integrity error here
            # because all items were aggregated by name
            self.create(
                name=name,
                quantity=item['quantity'],
                amount=item['amount'],
                date=date.date(),
                bill=bill)
            logger.debug(
                'Created item with name %s details %s' % (
                name, item)) 


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
        verbose_name='Total amount of all items in this spendings',
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
