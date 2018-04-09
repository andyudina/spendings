"""
Helpers for spendings apis tests (python and rest)
"""
import datetime
from mock import patch

from apps.bills.tests.helpers import TestBillMixin
from apps.spendings.models import Spending


class TestSpendingsMixin(TestBillMixin):
    """
    Helper for spenidngs tests
    """

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
                'amount': 30.0,
                'date': datetime.datetime(2018, 4, 5),
                'bill': bill_1
            },
            {
                'name': 'test-1',
                'quantity': 4,
                'amount': 40.0,
                'date': datetime.datetime(2018, 4, 6),
                'bill': bill_2
            },
            {
                'name': 'test-2',
                'quantity': 2,
                'amount': 40.0,
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
                'amount': 210.0,
                'date': datetime.datetime(2018, 1, 5),
                'bill': bill_3
            },
        ]
        for spending_dict in SPENDINGS:
            Spending.objects.create(
                **spending_dict)    