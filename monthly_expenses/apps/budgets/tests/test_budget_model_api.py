"""
Test python API for budget models
"""
import datetime
from mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.bills.models import Bill
from apps.bills.tests.helpers import (
    TestBillMixin, BillTestCase)
from apps.budgets.models import (
    Budget, TotalBudget,
    BillCategory, Category)


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


class TestBudgetAmountsValidation(
        TestBillMixin,
        TestCase):
    """
    Test that we do not save budget models
    if total budget amount is less than sum of
    categorised amounts
    """
    def setUp(self):
        self.user = self.get_or_create_user()
        self.category = Category.objects.create(name='test')
        self.total_budget = TotalBudget.objects.create(
            user=self.user,
            amount=100)
        self.categorical_budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=10)

    def test_budget_total_amount_is_too_little_can_not_update_total_budget(
            self):
        """
        we raise ValidationError if total budget amount is less than
        sum of categorical budgets
        """
        with self.assertRaises(ValidationError):
            self.total_budget.amount = 5
            self.total_budget.save(
                update_fields=['amount', ])

    def test_budget_total_amount_is_valid_can_update_total_budget(
            self):
        """
        we can update total budget if its amount is bigger than
        sum of categorical budgets
        """
        self.total_budget.amount = 105
        self.total_budget.save(
            update_fields=['amount', ])
        self.total_budget.refresh_from_db()
        self.assertEqual(
            self.total_budget.amount, 105)

    def test_budget_total_amount_is_too_small_can_t_update_categorical_budget(
            self):
        """
        we raise ValidationError if total budget amount is less than
        sum of categorical budgets
        """
        with self.assertRaises(ValidationError):
            self.categorical_budget.amount = 105
            self.categorical_budget.save(
                update_fields=['amount', ])

    def test_budget_total_amount_is_valid_can_update_categorical_budget(
            self):
        """
        we can update total budget if its amount is bigger than
        sum of categorical budgets
        """
        self.categorical_budget.amount = 5
        self.categorical_budget.save(
            update_fields=['amount', ])
        self.categorical_budget.refresh_from_db()
        self.assertEqual(
            self.categorical_budget.amount, 5)

    def test_categorised_amount_is_half_of_total_can_update_categorical_budget(
            self):
        """
        we can update total budget if its amount is bigger than
        sum of categorical budgets and one of the categorical budgets
        has an amount is more than half of total budget amount.
        """
        # We need to test this case to make sure
        # our logic with exluding current budget works
        new_amount = self.total_budget.amount * 2 / 3
        self.categorical_budget.amount = new_amount
        self.categorical_budget.save(
            update_fields=['amount', ])
        self.categorical_budget.amount = new_amount
        self.categorical_budget.save(
            update_fields=['amount', ])
        self.categorical_budget.refresh_from_db()
        self.assertEqual(
            self.categorical_budget.amount, 
            new_amount)
