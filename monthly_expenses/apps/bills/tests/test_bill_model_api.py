"""
Tests for python API of apps.bills.models.Bill model
"""
from hashlib import sha256

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.bills.models import Bill

from .check_image import CHECK_IMAGE as DEFAULT_CHECK_IMAGE



class BillPythonAPITestCase(TestCase):
    """
    Test domain logic for Bill model
    """

    def create_bill(self):
        """
        Helper to create a check image with predefined content
        """
        return Bill.objects.create(
                image=SimpleUploadedFile(
                    name='test_bill_image.jpg', 
                    content=DEFAULT_CHECK_IMAGE, 
                    content_type='image/jpeg'))

    def calculate_expected_hash(self):
        """
        Helper to calculate hash of predefined image
        """
        image_hash = sha256()
        image_hash.update(DEFAULT_CHECK_IMAGE)
        return image_hash.hexdigest()

    def test_create_bill__hash_saved(self):
        """
        We save sha256 for bill image on creation
        """
        bill = self.create_bill()
        expected_hash = self.calculate_expected_hash()
        self.assertEqual(
            bill.sha256_hash_hex, expected_hash)
