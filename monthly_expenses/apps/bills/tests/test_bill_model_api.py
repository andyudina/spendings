"""
Tests for python API of apps.bills.models.Bill model
"""
from mock import Mock, patch

from django.test import TestCase, override_settings

from apps.bills.models import Bill
from .helpers import TestBillMixin


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

@override_settings(PARSER='test_parser')
class BillPythonAPITestCase(
        TestBillMixin, TestCase):
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
        image_to_string_mock.return_value = TEST_PARSED_TEXT
        open_mock.return_value = Mock()

        bill = self.create_bill()
        bill_data = bill.parse_bill()
        self.assertEqual(
            bill_data, {
                "date": "2017-04-07 00:00:00", 
                "items": [
                    {
                        "item": "HAIR DRYER", 
                        "amount": 79.99, 
                        "quantity": 1
                    }
                ]})
