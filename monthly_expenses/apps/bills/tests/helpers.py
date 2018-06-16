"""
Test tools for bill app
"""
from hashlib import sha256

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.bills.models import Bill

from .check_image import CHECK_IMAGE as DEFAULT_CHECK_IMAGE


class TestBillMixin(object):
    """
    Mixin with test tools for bills app
    """
    def get_or_create_user(
            self, email=None):
        email = email or 'test@test.com'
        user, _ = User.objects.get_or_create(
            username=email,
            email=email,
            password='#')
        return user

    def create_bill(
            self, user=None, content=None):
        """
        Helper to create a check image with predefined content
        """
        content = content or DEFAULT_CHECK_IMAGE
        user = user or self.get_or_create_user()
        return Bill.objects.create(
                user=user,
                image=SimpleUploadedFile(
                    name='test_check.jpg',
                    content=content,
                    content_type='image/jpeg'))

    def calculate_expected_hash(self):
        """
        Helper to calculate hash of predefined image
        """
        image_hash = sha256()
        image_hash.update(DEFAULT_CHECK_IMAGE)
        return image_hash.hexdigest()

    def create_categories_for_bill(
            self, bill):
        """
        Helper to create categories and link them to bill
        """
        from apps.budgets.models import (
            Category, BillCategory)
        CATEGORIES = [
            {
                'category': {
                    'id': 1,
                    'name': 'a-test'
                },
                'id': 1,
                'amount': 10
            },
            {
                'category': {
                    'id': 2,
                    'name': 'b-test'
                },
                'id': 2,
                'amount': 20
            },
        ]
        for category in CATEGORIES:
            (category_obj, _) = \
                 Category.objects.get_or_create(**category['category'])
            Category.objects.\
                filter(id=category_obj.id).\
                update(**category['category'])
            category_obj = Category.objects.get(
                id=category['category']['id'])
            category_to_bill = BillCategory.objects.create(
                bill=bill,
                category=category_obj,
                amount=category['amount'])
            BillCategory.objects.\
                filter(id=category_to_bill.id).\
                update(id=category['id'])


class BillTestCase(
        TestBillMixin, TestCase):
    """
    Base test case class for bills
    """

    def tearDown(self):
        # manualluy delete bills
        # to force their media to be deleted also
        Bill.objects.all().delete()    
 