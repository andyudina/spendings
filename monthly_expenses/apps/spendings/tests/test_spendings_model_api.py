# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from mock import patch

from django.test import TestCase

from apps.spendings.models import Spending
from .helpers import TestSpendingsMixin


class SpendingModelAPITestCase(
        TestSpendingsMixin, TestCase):
    """
    Test python api for spendings model
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

class SpendingCreationTestCase(
        TestSpendingsMixin, TestCase):
    """
    Test creation of spendings on bills creation
    """

    PARSED_BILL_INFO = {
        'date': '2017-04-07 00:00:00', 
        'items': [
            {
                'item': 'test-1', 
                'amount': 10.10, 
                'quantity': 1
            },
            {
                'item': 'test-1', 
                'amount': 10.10, 
                'quantity': 1
            }
        ]
    }

    @patch('apps.bills.models.Bill.parse_bill')
    def test_bill_successfully_created__spendings_saved(
            self, parse_bill_mock):
        """
        We create spendings automatically on bill creation
        """
        parse_bill_mock.return_value = self.PARSED_BILL_INFO
        bill = self.create_bill()
        self.assertTrue(
            Spending.objects.filter(
                    date=datetime.date(2017, 4, 7),
                    name='test-1',
                    amount=20.20,
                    quantity=2,
                    bill=bill
                ).exists())

    @patch('apps.bills.models.Bill.parse_bill')
    def test_bill_successfully_created__spendings_name_changed_to_lowercase(
            self, parse_bill_mock):
        """
        We create spendings with item name in lowercase
        """
        parse_bill_mock.return_value = {
            'date': '2017-04-07 00:00:00', 
            'items': [
                {
                    'item': 'TEST-1', 
                    'amount': 10.10, 
                    'quantity': 1
                },
            ]
        }
        bill = self.create_bill()
        self.assertTrue(
            Spending.objects.filter(
                    date=datetime.date(2017, 4, 7),
                    name='test-1',
                    amount=10.10,
                    quantity=1,
                    bill=bill
                ).exists())

    @patch('apps.bills.models.Bill.parse_bill')
    def test_bill_can_not_be_parsed__spendings_not_created(
            self,  parse_bill_mock):
        """
        We don't create spendings if bill can not be parsed
        """
        parse_bill_mock.side_effect = \
            ValueError('Can not be parsed')
        self.create_bill()
        self.assertFalse(Spending.objects.exists())

    @patch('apps.bills.models.Bill.parse_bill')
    def test_bill_was_already_parsed__spendings_are_not_created_twice(
            self, parse_bill_mock):
        """
        We don't create bills duplicates
        """
        from apps.bills.models import Bill
        from apps.bills.signals import bill_was_created
        parse_bill_mock.return_value = self.PARSED_BILL_INFO
        bill = self.create_bill()
        # send signal second time
        bill_was_created.send(
            sender=Bill,
            bill=bill)
        self.assertEqual(
            Spending.objects.filter(
                    date=datetime.date(2017, 4, 7),
                    name='test-1',
                    amount=20.20,
                    quantity=2,
                    bill=bill
                ).count(), 1)
