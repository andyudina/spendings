# -*- coding: utf-8 -*-
"""
Test python api for spendings model
"""
import datetime
from mock import patch

from django.test import TestCase

from apps.spendings.models import Spending
from .helpers import SpendingsTestCase


class SpendingAggregationAPITestCase(
        SpendingsTestCase):
    """
    Test python api for spendings aggregation
    """

    def setUp(self):
        self.create_spendings()

    def test_speding_aggregation_all_spendings(self):
        """
        Python API for spending aggregation 
        without filtering by spending date
        """
        aggregation = Spending.objects.get_spendings_in_time_frame()
        self.assertListEqual(
                list(aggregation),
                [
                    {
                        'name': 'test-3',
                        'total_amount': 210,
                        'total_quantity': 10,
                        'bills_number': 1,
                    },
                    {
                        'name': 'test-1',
                        'total_amount': 70,
                        'total_quantity': 7,
                        'bills_number': 2,
                    },
                    {
                        'name': 'test-2',
                        'total_amount': 60,
                        'total_quantity': 3,
                        'bills_number': 2,
                    },
                ])

    def test_speding_aggregation_with_filter_by_date(self):
        """
        Python API for spending aggregation 
        with filtering by spending date
        """
        aggregation = Spending.objects.get_spendings_in_time_frame(
            begin_time=datetime.datetime(2018, 4, 4))
        self.assertListEqual(
                list(aggregation),
                [
                    {
                        'name': 'test-1',
                        'total_amount': 70,
                        'total_quantity': 7,
                        'bills_number': 2,
                    },
                    {
                        'name': 'test-2',
                        'total_amount': 60,
                        'total_quantity': 3,
                        'bills_number': 2,
                    },
                ])


class RewriteSpendingsAPITestCase(
        SpendingsTestCase):
    """
    Test python api for rewriting bill spendings
    """
    def setUp(self):
        self.bill = self.create_bill()

    def test_rewriting_spendings_preaggregated_spendings_created(self):
        """
        We preaggregate spendings before saving rewrited spendings 
        """
        items = [
            {
                'item': 'test-1',
                'quantity': 2,
                'amount': 20.20
            },
            {
                'item': 'test-1',
                'quantity': 10,
                'amount': 101
            }
        ]
        date = datetime.datetime(2018, 6, 6)
        Spending.objects.\
            rewrite_spendings_for_bill(self.bill, date, items)
        self.assertTrue(
            Spending.objects.filter(
                name='test-1',
                quantity=12,
                amount=121.20,
                date=date.date(),
                bill=self.bill).exists())

    def test_rewriting_spendings__item_name_changed_to_lowercase(self):
        """
        We save all spendings name in lowercase
        """
        items = [
            {
                'item': 'TEST-1',
                'quantity': 1,
                'amount': 10.10
            }
        ]
        date = datetime.datetime(2018, 5, 6)
        Spending.objects.\
            rewrite_spendings_for_bill(self.bill, date, items)
        self.assertTrue(
            Spending.objects.filter(
                name='test-1',
                quantity=1,
                amount=10.10,
                date=date.date(),
                bill=self.bill).exists())

    def test_rewriting_spendings_previous_spendings_deleted(self):
        """
        We delete previous spendings when rewrite spendings for bill
        """
        items = [
            {
                'item': 'TEST-1',
                'quantity': 1,
                'amount': 10.10
            }
        ]
        date = datetime.datetime(2018, 5, 6)       
        previous_spending = Spending.objects.create(
            name='test-0',
            quantity=1,
            amount=10.10,
            date=date.date(),
            bill=self.bill)
        Spending.objects.\
            rewrite_spendings_for_bill(self.bill, date, items)
        self.assertFalse(
            Spending.objects.\
                filter(id=previous_spending.id).\
                exists())       

    @patch(
        'apps.spendings.models.aggregate_spendings_by_name')
    def test_rewriting_spendings_error_raised__previous_spendings_were_not_deleted(
            self, aggregate_spendings_by_name_mock):
        """
        We rollback deletion of previous spendings if we fail to create new one
        """
        aggregate_spendings_by_name_mock.side_effect = ValueError('Just for tests')
        items = [
            {
                'item': 'TEST-1',
                'quantity': 1,
                'amount': 10.10
            }
        ]
        date = datetime.datetime(2018, 5, 6)       
        previous_spending = Spending.objects.create(
            name='test-0',
            quantity=1,
            amount=10.10,
            date=date.date(),
            bill=self.bill)
        # check that mock worked
        with self.assertRaises(ValueError):
            Spending.objects.\
                rewrite_spendings_for_bill(self.bill, date, items)
        # check that object was not deleted
        self.assertTrue(
            Spending.objects.\
                filter(id=previous_spending.id).\
                exists())
