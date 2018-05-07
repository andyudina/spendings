"""
Test for REST API for bills
"""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from apps.bills.api import IMAGE_ALREADY_UPLOADED_ERROR
from apps.bills.models import Bill
from .check_image import CHECK_IMAGE as DEFAULT_CHECK_IMAGE
from .helpers import BillTestCase


class BillRestAPITest(BillTestCase):
    """
    Test rest api endpoints for uploading and managing bills
    """
    def setUp(self):
        self.user = self.get_or_create_user()

    def upload_bill(
            self, auth_needed=True):
        """
        Helper to upload bill via api
        """
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.post(
            reverse('bill'),
            {
                'image': SimpleUploadedFile(
                    name='test_check.jpg', 
                    content=DEFAULT_CHECK_IMAGE, 
                    content_type='image/jpeg')
            },
            format='multipart')

    def test_upload_bill__successfull_response(self):
        """
        We return 201 created when bill is successfully uploaded
        """
        response = self.upload_bill()
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED)

    def test_upload_bill__bill_created(self):
        """
        We create a bill instanse after successful upload
        """
        self.upload_bill()
        self.assertTrue(
            Bill.objects.filter(
                sha256_hash_hex=self.calculate_expected_hash()).exists())

    def test_upload_bill__creator_saved(self):
        """
        We save bill creator
        """
        self.upload_bill()
        bill = Bill.objects.get(
                sha256_hash_hex=self.calculate_expected_hash())
        self.assertTrue(
            bill.user, self.user)

    def test_upload_bill__parsed_bill_returned(self):
        """
        We return parsed bill info after successful upload
        """
        response = self.upload_bill()
        bill = Bill.objects.latest('create_time')
        self.assertEqual(
            response.data, 
            {
                'bill': bill.id,
            })

    def test_upload_bill_already_exists__existing_bill_returned(self):
        """
        We return existing bill if bill was already uploaded
        """
        bill = self.create_bill()
        response = self.upload_bill()  
        self.assertDictEqual(
            response.data,
            {
                'bill': bill.id
            })

    def test_upload_bill_already_exists__ok_response_returned(self):
        """
        We return 200 OK if bill was already uploaded
        """
        self.create_bill()
        response = self.upload_bill()  
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_not_authenticated_tries_load_bill__error_returned(self):
        """
        We return 403 forbidden if user is not logged in
        while he is trying to create a bill
        """   
        response = self.upload_bill(
            auth_needed=False)
        self.assertEqual(
            response.status_code, 
            status.HTTP_403_FORBIDDEN)
