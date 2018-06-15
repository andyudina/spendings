"""
Tests for python API of apps.bills.models.Bill model
"""
from mock import Mock, patch

from apps.bills.models import Bill
from apps.budgets.models import Category
from .helpers import BillTestCase


TEST_PARSED_TEXT = '''
EXAMPLE RECEIPT NORMAL DAY

NEW OXFORD STREET STORE TEL: 020 7637 9348
9876543210

John Doe

New Oxford Street

London

WC1A1HB

Transaction: 982747438928 on 4.07.17 at 13.24

You were served today by Jane S

E
HAIR DRYER 1 @ 20.00 , 79.99
123456 VAT @ 20%
E
Total Amount Ex. VAT 79.99
VAT 1600
Total amount due Inc. VAT 95.99

Cash 95.99

Thank you for shopping with us
Our full range is available 24/7 at
salon-services.com
----------------------------------------------------------------------
'''

class BillPythonAPITestCase(BillTestCase):
    """
    Test domain logic for Bill model
    """

    def test_create_bill__hash_saved(self):
        """
        We save sha256 for bill image on creation
        """
        bill = self.create_bill()
        expected_hash = self.calculate_expected_hash()
        self.assertEqual(
            bill.sha256_hash_hex, expected_hash)

    @patch(
        'apps.bills.models.Image.open')
    @patch(
        'apps.bills.models.image_to_string')
    def test_parse_bill__valid_data_returned(
            self, 
            image_to_string_mock,
            open_mock):
        """
        We return valid datetime and sepndings when parse bill

        TODO: test different bill formats and scenarios
        """
        # set up test backend
        from apps.bills import models
        from apps.bills.parsers import TestParser
        models.parser = TestParser()

        image_to_string_mock.return_value = TEST_PARSED_TEXT
        open_mock.return_value = Mock()

        bill = self.create_bill()
        bill_data = bill.parse_bill()
        self.assertEqual(
            bill_data, {
                "date": "2017-07-04 00:00:00", 
                "items": [
                    {
                        "name": "HAIR DRYER", 
                        "amount": 79.99, 
                        "quantity": 1
                    }
                ]})

    @patch(
        'apps.bills.models.Image.open')
    def test_parse_bill__io_error_rerased_as_value_error(
            self, 
            open_mock):
        """
        We reraise IOError as value error
        """
        open_mock.side_effect = IOError('not found')

        bill = self.create_bill()
        with self.assertRaises(ValueError):
            bill.parse_bill()

    def test_category_linking_in_bulk__success(self):
        """
        We create categories to bill links in bulk
        if format of passed data is correct
        """
        category = Category.objects.create(name='test')
        bill = self.create_bill()
        bill.create_categories_in_bulk([{
                'category': {
                    'id': category.id,
                },
                'amount': 10
            }])
        self.assertTrue(
            bill.categories.filter(id=category.id))

    def test_category_linking_in_bulk__error_raised_if_category_does_not_exist(
            self):
        """
        We raise ObjectNotFound error if any passed category
        does not exist
        """
        bill = self.create_bill()
        with self.assertRaises(Category.DoesNotExist):
            bill.create_categories_in_bulk([
                {
                    'category': {
                        'id': 10,
                    },
                    'amount': 10
                }
            ])

    def test_category_linking_in_bulk__error_raised_for_duplicates(
            self):
        """
        We raise IntegrityError if we try to create duplicated links
        """
        from django.db import IntegrityError
        category = Category.objects.create(name='test')
        bill = self.create_bill()
        with self.assertRaises(IntegrityError):
            bill.create_categories_in_bulk([
                {
                    'category': {
                        'id': category.id,
                    },
                    'amount': 10
                },
                {
                    'category': {
                        'id': category.id,
                    },
                    'amount': 10
                }
            ])
