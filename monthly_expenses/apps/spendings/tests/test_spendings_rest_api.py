"""
Test REST APIs for spendings
"""
import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from .helpers import TestSpendingsMixin


class SpendingRestAPITestCase(
        TestSpendingsMixin, TestCase):
    """
    Test rest api for spendings
    """

    def setUp(self):
        self.create_spendings()

    def get_aggregated_by_name_spendings(
            self, begin_time=None, end_time=None):
        get_request = {}
        if begin_time:
            get_request['begin_time'] = begin_time
        if end_time:
            get_request['end_time'] = end_time
        return self.client.get(
            reverse('spendings-aggregated-by-name'),
            get_request)

    def test_aggregated_by_name_spendings__ok_response_returned(self):
        """
        We return 200 OK response on valid request
        """
        response = self.get_aggregated_by_name_spendings()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_aggregated_by_name_spendings__aggregated_spendings_returned(self):   
        """
        We return aggregated by name spendinsg in given time frame
        """
        response = self.get_aggregated_by_name_spendings(
            begin_time=datetime.date(2018, 4, 4))
        self.assertEqual(
            response.data,
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
