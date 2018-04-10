"""
Test tools for bill app
"""
from hashlib import sha256

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.bills.models import Bill

from .check_image import CHECK_IMAGE as DEFAULT_CHECK_IMAGE


class TestBillMixin(object):
    """
    Mixin with test tools for bills app
    """

    def create_bill(self):
        """
        Helper to create a check image with predefined content
        """
        return Bill.objects.create(
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
 