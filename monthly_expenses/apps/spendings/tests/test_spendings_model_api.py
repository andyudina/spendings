# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from mock import patch

from django.test import TestCase

from apps.bills.tests.helpers import TestBillMixin
from apps.spendings.models import Spending


class SpendingModelAPITestCase(
        TestBillMixin, TestCase):
    """
    Test python api for spendings model
    """

    def setUp(self):
        self.create_spendings()

    @patch(
        'apps.bills.handlers.generate_hash_from_image')
    def create_bill_with_mock_hash(
            self, bill_hash, 
            generate_hash_from_image_mock):
        generate_hash_from_image_mock.return_value = bill_hash
        return self.create_bill()

    def create_spendings(self):
        bill_1 = self.create_bill_with_mock_hash('bill-1')
        bill_2 = self.create_bill_with_mock_hash('bill-2')
        bill_3 = self.create_bill_with_mock_hash('bill-3')

        SPENDINGS = [
            {
                'name': 'test-1',
                'quantity': 3,
                'amount': 10.0,
                'date': datetime.datetime(2018, 4, 5),
                'bill': bill_1
            },
            {
                'name': 'test-1',
                'quantity': 4,
                'amount': 10.0,
                'date': datetime.datetime(2018, 4, 6),
                'bill': bill_2
            },
            {
                'name': 'test-2',
                'quantity': 2,
                'amount': 20.0,
                'date': datetime.datetime(2018, 4, 5),
                'bill': bill_1
            },
            {
                'name': 'test-2',
                'quantity': 1,
                'amount': 20.0,
                'date': datetime.datetime(2018, 4, 6),
                'bill': bill_2
            },
            {
                'name': 'test-3',
                'quantity': 10,
                'amount': 21.0,
                'date': datetime.datetime(2018, 1, 5),
                'bill': bill_3
            },
        ]
        for spending_dict in SPENDINGS:
            Spending.objects.create(
                **spending_dict)


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
