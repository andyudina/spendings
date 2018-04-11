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
        self.user = self.get_or_create_user()
        self.create_spendings()

    def test_speding_aggregation_all_spendings(self):
        """
        Python API for spending aggregation 
        without filtering by spending date
        """
        aggregation = Spending.objects.\
            get_spendings_in_time_frame(
                user=self.user)
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
                        'total_amount': 30,
                        'total_quantity': 15,
                        'bills_number': 2,
                    },
                ])

    def test_speding_aggregation_with_filter_by_date(self):
        """
        Python API for spending aggregation 
        with filtering by spending date
        """
        aggregation = Spending.objects.get_spendings_in_time_frame(
            self.user,
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
                        'total_amount': 30,
                        'total_quantity': 15,
                        'bills_number': 2,
                    },
                ])

    def test_speding_aggregation__sort_by_quantity(self):
        """
        Python API for spending aggregation 
        with sorting by quantity
        """
        aggregation = Spending.objects.get_spendings_in_time_frame(
            self.user,
            begin_time=datetime.datetime(2018, 4, 4),
            sort_by='quantity')
        self.assertListEqual(
                list(aggregation),
                [
                    {
                        'name': 'test-2',
                        'total_amount': 30,
                        'total_quantity': 15,
                        'bills_number': 2,
                    },            
                    {
                        'name': 'test-1',
                        'total_amount': 70,
                        'total_quantity': 7,
                        'bills_number': 2,
                    },
                ])

    def test_speding_aggregation__wrong_sort_by_error_raised(self):
        """
        Python API for spending aggregation 
        raise assertyion error is unsupported sort is requested
        """
        with self.assertRaises(AssertionError):
            aggregation = Spending.objects.get_spendings_in_time_frame(
                self.user,
                begin_time=datetime.datetime(2018, 4, 4),
                sort_by='not-supported')

    def test_spendings_aggregation__filter_by_user(self):
        """
        We filter out spendings that was not created by
        passed user
        """
        new_user =\
            self.get_or_create_user(
                email='test-1@test.com')
        new_bill = self.create_bill(user=new_user)
        spending = Spending.objects.create(
            date=datetime.date(2018, 6, 6),
            bill=new_bill,
            name='new-test-1',
            amount=10.10,
            quantity=1)
        aggregation = Spending.objects.\
            get_spendings_in_time_frame(new_user)
        self.assertListEqual(
            list(aggregation), 
            [
                {
                    'name': 'new-test-1',
                    'total_amount': 10.1,
                    'total_quantity': 1,
                    'bills_number': 1,
                }
            ])


class SpendingTotalAPITestCase(
        SpendingsTestCase):
    """
    Test python api for calculation of total spendings
    """

    def setUp(self):
        self.user = self.get_or_create_user()
        self.create_spendings()

    def test_total_spendings(self):
        """
        Python API for total spendings calculation
        without filtering by spending date
        """
        aggregation = Spending.objects.\
            get_total_spendings_in_time_frame(
                user=self.user)
        self.assertDictEqual(
                aggregation,
                {
                    'total_amount': 310.0,
                    'total_quantity': 32,
                    'total_bills_number': 3,
                })

    def test_total_spendings_with_filter_by_date(self):
        """
        Python API for total spendings calculation
        with filtering by spending date
        """
        aggregation = Spending.objects.get_total_spendings_in_time_frame(
            self.user,
            begin_time=datetime.datetime(2018, 4, 4))
        self.assertDictEqual(
                aggregation,
                {
                    'total_amount': 100.0,
                    'total_quantity': 22,
                    'total_bills_number': 2,
                })

    def test_total_spendings__filter_by_user(self):
        """
        We filter out spendings that was not created by
        passed user
        """
        new_user =\
            self.get_or_create_user(
                email='test-1@test.com')
        new_bill = self.create_bill(user=new_user)
        spending = Spending.objects.create(
            date=datetime.date(2018, 6, 6),
            bill=new_bill,
            name='new-test-1',
            amount=10.10,
            quantity=1)
        aggregation = Spending.objects.\
            get_total_spendings_in_time_frame(new_user)
        self.assertDictEqual(
            aggregation, 
            {
                'total_amount': 10.1,
                'total_quantity': 1,
                'total_bills_number': 1,
            })


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
