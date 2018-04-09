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
