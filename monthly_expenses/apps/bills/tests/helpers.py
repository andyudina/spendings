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

    def create_bill(self, user=None):
        """
        Helper to create a check image with predefined content
        """
        user = user or self.get_or_create_user()
        return Bill.objects.create(
                user=user,
                image=SimpleUploadedFile(
                    name='test_check.jpg', 
                    content=DEFAULT_CHECK_IMAGE, 
                    content_type='image/jpeg'))

    def calculate_expected_hash(self):
        """
        Helper to calculate hash of predefined image
        """
        image_hash = sha256()
        image_hash.update(DEFAULT_CHECK_IMAGE)
        return image_hash.hexdigest()


class BillTestCase(
        TestBillMixin, TestCase):
    """
    Base test case class for bills
    """

    def tearDown(self):
        # manualluy delete bills
        # to force their media to be deleted also
        Bill.objects.all().delete()    
 