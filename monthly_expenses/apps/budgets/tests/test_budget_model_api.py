"""
Test python API for budget models
"""
import datetime

from django.test import TestCase

from apps.bills.models import Bill
from apps.bills.tests.helpers import BillTestCase
from apps.budgets.models import (
    Budget, BillCategory, Category)


class CalculateTotalExpensesForBudgetTestCase(
        BillTestCase):
    """
    Test python api for summing total budget expenses
    """

    def setUp(self):
        self.user = self.get_or_create_user()
        self.category = Category.objects.create(name='test')
        self.bills = [
            self.create_bill(content='test-1'),
            self.create_bill(content='test-2'),
            self.create_bill(content='test-3')
        ]
        self.bills_to_categories = [
            BillCategory.objects.create(
                bill=self.bills[0],
                category=self.category,
                amount=10),
            BillCategory.objects.create(
                bill=self.bills[1],
                category=self.category,
                amount=20),
            BillCategory.objects.create(
                bill=self.bills[2],
                category=self.category,
                amount=30),
        ]
        Bill.objects.\
            filter(id=self.bills[0].id).\
            update(create_time=datetime.datetime(2018, 6, 1))
        Bill.objects.\
            filter(id=self.bills[1].id).\
            update(create_time=datetime.datetime(2018, 6, 10))
        Bill.objects.\
            filter(id=self.bills[2].id).\
            update(create_time=datetime.datetime(2018, 6, 20))
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=100)

    def test_no_timelimits_valid_sum_returned(self):
        """
        We calculate valid sum if no time limits passed
        """
        self.assertEqual(
            self.budget.calculate_total_expenses(),
            60)

    def test_filter_bills_by_budgeting_period_begin_date__valid_sum_returned(
            self):
        """
        We calculate valid sum if begin date passed
        """
        self.assertEqual(
            self.budget.calculate_total_expenses(
                begin_date=datetime.datetime(2018, 6, 9)
            ),
            50)

    def test_filter_bills_by_budgeting_period_end_date__valid_sum_returned(
            self):
        """
        We calculate valid sum if end date passed
        """
        self.assertEqual(
            self.budget.calculate_total_expenses(
                end_date=datetime.datetime(2018, 6, 11)
            ),
            30)

    def test_filter_out_bills_with_different_category(self):
        """
        We do not include bills for different category into aggregation
        """
        new_category = Category.objects.create(
            name='test-1')
        self.bills_to_categories[0].category = new_category
        self.bills_to_categories[0].save(update_fields=['category'])
        self.assertEqual(
            self.budget.calculate_total_expenses(),
            50)

    def test_filter_out_bills_with_different_user(self):
        """
        We do not include bills for different user into aggregation
        """
        new_user = self.get_or_create_user(email='test-2@test.com')
        self.bills[2].user = new_user
        self.bills[2].save(update_fields=['user'])
        self.assertEqual(
            self.budget.calculate_total_expenses(),
            30)

    def test_no_bills_found__zero_returned(self):
        """
        We return zero if no bills were found
        """
        self.assertEqual(
            self.budget.calculate_total_expenses(
                begin_date=datetime.datetime(2018, 6, 30)
            ),
            0)
