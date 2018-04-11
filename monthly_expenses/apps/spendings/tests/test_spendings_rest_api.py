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
        self.user = self.get_or_create_user()
        self.create_spendings()

    def get_aggregated_by_name_spendings(
            self, 
            begin_time=None, end_time=None,
            need_auth=True, user=None):
        get_request = {}
        if begin_time:
            get_request['begin_time'] = begin_time
        if end_time:
            get_request['end_time'] = end_time
        if need_auth:
            self.client.force_login(user or self.user)
        return self.client.get(
            reverse('spendings-aggregated-by-name'),
            get_request)

    def test_aggregated_by_name_spendings__no_date_ok_response_returned(self):
        """
        We return 200 OK response on valid request without dates
        """
        response = self.get_aggregated_by_name_spendings()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_pass_wrong_date__bad_request_response_returned(self):
        """
        We return 400 bad request response if date can nit be parsed
        """
        response = self.get_aggregated_by_name_spendings(
            begin_time='not-a-datetime')
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_user_not_login__403_response_returned(self):
        """
        We return 403 forbidden response if user is not logined
        """
        response = self.get_aggregated_by_name_spendings(
            need_auth=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_not_user_spendings_are_filtered_out(self):
        """
        We do not include spendings from other users
        to result set
        """
        new_user =\
            self.get_or_create_user(
                email='test-1@test.com')
        new_bill = self.create_bill(user=new_user)
        # retrieve spendings for new_user
        response = self.get_aggregated_by_name_spendings(
            user=new_user)
        self.assertDictEqual(
            response.data, {
                'total': {
                    'total_bills_number': 0,
                    'total_quantity': 0,
                    'total_amount': 0,
                },
                'spendings': []
            })       

    def test_aggregated_by_name_spendings__aggregated_spendings_returned(self):   
        """
        We return aggregated by name spendinsg in given time frame
        """
        response = self.get_aggregated_by_name_spendings(
            begin_time=datetime.date(2018, 4, 4))
        self.assertDictEqual(
            response.data,
            {
                'spendings': [
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
                ],
                'total': {
                    'total_bills_number': 2,
                    'total_quantity': 22,
                    'total_amount': 100,
                }
            })


class RewriteSpendinRestAPITestCase(
        SpendingsTestCase):
    """
    Test rest api to rewrite spendings
    """

    def setUp(self):
        self.user = self.get_or_create_user()
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
            self, 
            bill=None, date=None, items=None,
            need_auth=True, user=None):
        bill = bill or self.bill.id
        date = date or self.date
        items = items if items is not None else self.items
        data = {
            'bill': bill,
            'date': date,
            'items': items
        }
        if need_auth:
            self.client.force_login(user or self.user)
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

    def test_user_is_not_logged_in__forbidden_returned(self):
        """
        We return 403 forbidden if user is not logged in
        """
        response = self.rewrite_spendings_for_bill(
            need_auth=False)
        self.assertEqual(
            response.status_code, 
            status.HTTP_403_FORBIDDEN)     

    def test_user_tries_to_modify_another_user_spendings__forbidden_returned(self):
        """
        We return 403 forbidden if user tries to access another user bill
        """
        new_user = self.get_or_create_user(
            email='new-test-1@test.com')
        response = self.rewrite_spendings_for_bill(
            user=new_user)
        self.assertEqual(
            response.status_code, 
            status.HTTP_403_FORBIDDEN) 
