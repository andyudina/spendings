"""
Test REST API for budgets
"""
import datetime
from mock import patch, Mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from apps.bills.models import Bill
from apps.bills.tests.helpers import BillTestCase
from apps.budgets.models import (
    TotalBudget, Budget, BillCategory, Category)
from .helpers import BudgetTestCaseMixin


class CategoryApiTestCase(TestCase):
    """
    Test REST API for categories
    """

    def setUp(self):
        CATEGORIES = [
            {
                'name': 'b-test',
                'id': 1,
            },
            {
                'name': 'a-test',
                'id': 2,
            },
            {
                'name': 'c-test',
                'id': 3,
            },
        ]
        for category in CATEGORIES:
            category_obj = Category.objects.create(**category)
            Category.objects.\
                filter(id=category_obj.id).\
                update(id=category['id'])

    def list_categories(self):
        return self.client.get(
            reverse('list-categories'))

    def test_list_categories__200_ok_returned(self):
        """
        We return 200 OK status on categories request
        """
        response = self.list_categories()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_list_categories__all_categories_returned_sorted(self):
        """
        We return all categories in one list sorted  by names
        """
        response = self.list_categories()
        self.assertListEqual(
            response.data,
            [
                {
                    'name': 'a-test',
                    'id': 2,
                },
                {
                    'name': 'b-test',
                    'id': 1,
                },
                {
                    'name': 'c-test',
                    'id': 3,
                },
            ])


class CreateBudgetAPITestCase(
        BudgetTestCaseMixin,
        TestCase):
    """
    Test REST API for budget creation
    """

    def setUp(self):
        self.user = self.get_or_create_user_with_budget()
        self.category = Category.objects.create(
            name='test')

    def create_budget(
            self, 
            auth_needed=True,
            category=None, amount=None):
        category = category or self.category.id
        amount = amount or 10
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.post(
            reverse('budgets'),
            {
                'category': category,
                'amount': amount,
            })

    def test_create_budget__201_created_returned(self):
        """
        We return 201 CREATED status if budget created successfully
        """
        response = self.create_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_create_budget_succesfully(self):
        """
        Budget created on successfull request
        """
        response = self.create_budget()
        self.assertTrue(
            Budget.objects.filter(
                user=self.user,
                category=self.category,
                amount=10).exists())

    def test_create_budget_non_authenticated__error_returned(self):
        """
        We return 403 FORBIDDEN status if user is not authenticated
        """
        response = self.create_budget(auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_create_budget_non_existing_category__error_returned(self):
        """
        We return 400 bad request if category does not exists
        """
        response = self.create_budget(
            category=self.category.id + 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_create_budget_twice__error_returned(self):
        """
        We return 400 bad request if budget
        for this category was already created
        """
        Budget.objects.create(
            category=self.category,
            user=self.user,
            amount=10)
        response = self.create_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)


class ListBudgetAPITestCase(
        BudgetTestCaseMixin,
        BillTestCase,
        TestCase):
    """
    Test REST API for budgets listing
    """
    def setUp(self):
        self.user = self.get_or_create_user_with_budget()
        self.bill = self.create_bill()
        self.category = Category.objects.create(name='test')
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=100)
        self.bill_to_category = BillCategory.objects.create(
            bill=self.bill,
            category=self.category,
            amount=10)
        Bill.objects.filter(id=self.bill.id).\
            update(create_time=datetime.datetime(2018, 6, 9))

    def list_budgets(
            self,
            auth_needed=True):
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.get(
            reverse('budgets'))

    def test_list__200_ok_returned(self):
        """
        We return 200 OK status on successfull request
        """
        response = self.list_budgets()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    @patch('apps.budgets.models.datetime')
    def test_list_budgets_succesfully(
            self, datetime_mock):
        """
        Valid budget list returned
        """
        datetime_mock.date.today = Mock(
            return_value=datetime.date(2018, 6, 20))
        response = self.list_budgets()
        self.assertListEqual(
            response.data,
            [
                {
                    'amount': 100, 
                    'id': self.budget.id, 
                    'category': {
                        'id': self.category.id,
                        'name': 'test'
                    },
                    'total_expenses_in_current_month': 10
                }
            ])

    def test_list_budget_non_authenticated__error_returned(self):
        """
        We return 403 FORBIDDEN status if user is not authenticated
        """
        response = self.list_budgets(auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class UpdateBudgetAPITestCase(
        BudgetTestCaseMixin, TestCase):
    """
    Test REST API for budget updates
    """

    def setUp(self):
        self.user = self.get_or_create_user_with_budget()
        self.category = Category.objects.create(
            name='test')
        self.budget = Budget.objects.create(
            category=self.category,
            user=self.user,
            amount=200)

    def update_budget(
            self, 
            auth_needed=True,
            budget_id=None,
            data=None):
        import json
        data = data or {
            'amount': 100
        }
        budget_id = budget_id or self.budget.id
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.patch(
            reverse(
                'budget',
                kwargs={
                    'budget_id': budget_id
                }),
            json.dumps(data),
            content_type='application/json')

    def test_update_budget__200_returned(self):
        """
        We return 200 OK if budget updated successfully
        """
        response = self.update_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_update_budget__amount_changed(self):
        """
        We modify budget amount on successfull update
        """
        self.update_budget(
            data={
                'amount': 100
            })
        self.budget.refresh_from_db()
        self.assertEqual(
            self.budget.amount, 100)

    def test_update_budget_non_authenticated__error_returned(self):
        """
        We return 403 FORBIDDEN status if user is not authenticated
        """
        response = self.update_budget(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_update_budget_for_different_user__error_returned(self):
        """
        We return 403 FORBIDDEN status if user tries to update budget
        owned by another user
        """
        new_user = self.get_or_create_user_with_budget(
            email='test-new@gmai.com')
        self.budget.user = new_user
        self.budget.save(update_fields=['user', ])
        response = self.update_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_update_non_existing_budget__error_returned(self):
        """
        We return 404 not found status if user tries to update budget
        that does not exist
        """
        response = self.update_budget(
            budget_id=self.budget.id + 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_update_budget_category__ignored(self):
        """
        We ignore attempts to update budget category through this API
        """
        new_category = Category.objects.create(
            name='new-category')
        response = self.update_budget(
            data={
                'category': new_category.id,
                'amount': 100
            })
        # request went through
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.budget.refresh_from_db()
        # category hasn't changed
        self.assertEqual(
            self.budget.category,
            self.category)


class DeleteBudgetAPITestCase(
        BudgetTestCaseMixin, TestCase):
    """
    Test REST API to delete budget
    """

    def setUp(self):
        self.user = self.get_or_create_user_with_budget()
        self.user.total_budget.amount = 1000
        self.user.total_budget.save(
            update_fields=['amount', ])
        self.category = Category.objects.create(
            name='test')
        self.budget = Budget.objects.create(
            category=self.category,
            user=self.user,
            amount=200)

    def delete_budget(
            self, 
            auth_needed=True,
            budget_id=None):
        budget_id = budget_id or self.budget.id
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.delete(
            reverse(
                'budget',
                kwargs={
                    'budget_id': budget_id
                })
            )

    def test_delete_budget__204_returned(self):
        """
        We return 204 No content if budget deleted successfully
        """
        response = self.delete_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_delete_budget__amount_changed(self):
        """
        We successfully deleted budget
        """
        self.delete_budget()
        self.assertFalse(
            Budget.objects.filter(
                id=self.budget.id).exists())

    def test_delete_budget_non_authenticated__error_returned(self):
        """
        We return 403 FORBIDDEN status if user is not authenticated
        """
        response = self.delete_budget(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_delete_budget_for_different_user__error_returned(self):
        """
        We return 403 FORBIDDEN status if user tries to delete budget
        owned by another user
        """
        new_user = self.get_or_create_user_with_budget(
            email='test-new@gmai.com')
        self.budget.user = new_user
        self.budget.save(update_fields=['user', ])
        response = self.delete_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_delete_non_existing_budget__error_returned(self):
        """
        We return 404 not found status if user tries to update budget
        that does not exist
        """
        response = self.delete_budget(
            budget_id=self.budget.id + 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)


class RequestTotalBudgetAPITestCase(
         BudgetTestCaseMixin, TestCase):
    """
    Test API enpoint to show total budget
    """
    def setUp(self):
        self.user = self.get_or_create_user_with_budget()

    def get_total_budget(
            self, 
            auth_needed=True):
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.get(
            reverse('total-budget'))

    def test_get_total_budget__200_returned(self):
        """
        We return 200 OK on successful request
        """
        response = self.get_total_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_get_total_budget__valid_amount_returned(self):
        """
        We return valid budget amount
        """
        response = self.get_total_budget()
        self.assertDictEqual(
            response.data,
            {
                'amount': self.user.total_budget.amount
            })

    def test_get_total_budget_non_authenticated__error_returned(self):
        """
        We return 403 FORBIDDEN status if user is not authenticated
        """
        response = self.get_total_budget(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class UpdateTotalBudgetAPITestCase(
         BudgetTestCaseMixin, TestCase):
    """
    Test API enpoint to update total budget
    """
    def setUp(self):
        self.user = self.get_or_create_user_with_budget()

    def update_total_budget(
            self, 
            auth_needed=True,
            data=None):
        import json
        data = data or {
            'amount': 200
        }
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.patch(
            reverse('total-budget'),
            json.dumps(data),
            content_type='application/json')

    def test_update_total_budget__200_returned(self):
        """
        We return 200 OK if budget updated successfully
        """
        response = self.update_total_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_update_total_budget__amount_changed(self):
        """
        We modify total budget amount on successfull update
        """
        self.update_total_budget(
            data={
                'amount': 200
            })
        self.user.total_budget.refresh_from_db()
        self.assertEqual(
            self.user.total_budget.amount, 200)

    def test_update_total_budget_non_authenticated__error_returned(self):
        """
        We return 403 FORBIDDEN status if user is not authenticated
        """
        response = self.update_total_budget(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
