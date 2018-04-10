"""
Test REST APIs for spendings
"""
import datetime
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from apps.spendings.models import Spending
from .helpers import SpendingsTestCase


class SpendingAggregationRestAPITestCase(
        SpendingsTestCase):
    """
    Test rest api for spendings aggregation
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


class RewriteSpendinRestAPITestCase(
        SpendingsTestCase):
    """
    Test rest api to rewrite spendings
    """

    def setUp(self):
        self.date = '2018-06-05 00:00:00'
        self.bill = self.create_bill()
        self.items = [
            {
                'item': 'test-1',
                'quantity': 2,
                'amount': 20.20
            },
        ]

    def rewrite_spendings_for_bill(
            self, bill=None, date=None, items=None):
        bill = bill or self.bill.id
        date = date or self.date
        items = items if items is not None else self.items
        data = {
            'bill': bill,
            'date': date,
            'items': items
        }
        return self.client.post(
            reverse('rewrite-spendings'),
            json.dumps(data),
            content_type='application/json')

    def test_successfully_rewriten_spendings__ok_response_returned(self):
        """
        We return 201 created if new spendings were successfully created
        """
        response = self.rewrite_spendings_for_bill()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_successfully_create_spendings(self):
        """
        We successfully create new spendings
        """
        response = self.rewrite_spendings_for_bill()
        self.assertTrue(
            Spending.objects.filter(
                bill=self.bill,
                date=datetime.date(2018, 6, 5),
                name='test-1',
                quantity=2,
                amount=20.20).exists())

    def test_wrong_bill_id__bad_request_returned(self):
        """
        We return 400 response if bill can not be found
        """
        response = self.rewrite_spendings_for_bill(
            bill=self.bill.id + 1)
        self.assertIn(
            'bill', response.data)
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST)

    def test_unknown_date_format__bad_request_returned(self):
        """
        We return 400 response if date was passed in wrong format
        """
        response = self.rewrite_spendings_for_bill(date='03-04-2018')
        self.assertIn(
            'date', response.data)
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST)

    def test_empty_items__bad_request_returned(self):
        """
        We return 400 response if empty items were passe
        """
        response = self.rewrite_spendings_for_bill(items=[])
        self.assertIn(
            'items', response.data)
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST)
