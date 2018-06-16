"""
Test REST API for budgets
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from apps.budgets.models import (
    Budget, Category)


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


class CreateBudgetAPITestCase(TestCase):
    """
    Test REST API for budget creation
    """

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create(
            username='test@gmai.com',
            email='test@gmai.com',
            password='#')
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
        We return 200 OK status if budget created successfully
        """
        response = self.create_budget()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_create_budget_succesfully(self):
        """
        Budget created successfully on successfull request
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
