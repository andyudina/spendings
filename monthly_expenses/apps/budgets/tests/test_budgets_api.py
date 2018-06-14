"""
Test REST API for budgets
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from apps.budgets.models import Category

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
