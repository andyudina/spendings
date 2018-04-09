"""
Test for REST API for bills
"""
from mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status

from apps.bills.api import IMAGE_ALREADY_UPLOADED_ERROR
from apps.bills.models import Bill
from .check_image import CHECK_IMAGE as DEFAULT_CHECK_IMAGE
from .helpers import TestBillMixin


class BillRestAPITest(
        TestBillMixin, TestCase):
    """
    Test rest api endpoints for uploading and managing bills
    """

    def upload_bill(self):
        """
        Helper to upload bill via api
        """
        return self.client.post(
            reverse('bill'),
            {
                'image': SimpleUploadedFile(
                    name='test_check.jpg', 
                    content=DEFAULT_CHECK_IMAGE, 
                    content_type='image/jpeg')
            },
            format='multipart')
   
    @patch(
        'apps.bills.models.Bill.parse_bill')
    def test_upload_bill__successfull_response(
            self, parse_bill_mock):
        """
        We return 201 created when bill is successfully uploaded
        """
        parse_bill_mock.return_value = {}
        response = self.upload_bill()
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED)

    @patch(
        'apps.bills.models.Bill.parse_bill')
    def test_upload_bill__bill_created(
            self, parse_bill_mock):
        """
        We create a bill instanse after successful upload
        """
        parse_bill_mock.return_value = {}
        self.upload_bill()
        self.assertTrue(
            Bill.objects.filter(
                sha256_hash_hex=self.calculate_expected_hash()).exists())

    @patch(
        'apps.bills.models.Bill.parse_bill')
    def test_upload_bill__parsed_bill_returned(
            self, parse_bill_mock):
        """
        We return parsed bill info after successful upload
        """
        PARSED_BILL = {'test': 'test'}
        parse_bill_mock.return_value = PARSED_BILL
        response = self.upload_bill()
        self.assertEqual(
            response.data, PARSED_BILL)

    @patch(
        'apps.bills.models.Bill.parse_bill')
    def test_upload_bill_parsing_failed__error_returned(
            self, parse_bill_mock):
        """
        We raise error if failed to parse bill
        """
        PARSING_ERROR = 'Problem with parsing'
        parse_bill_mock.side_effect = ValueError(PARSING_ERROR)
        response = self.upload_bill()
        self.assertEqual(
            response.data, 
            {
                'error': PARSING_ERROR
            })
        self.assertEqual(
            response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_upload_bill_already_exists__error_returned(self):
        """
        We raise error if bill aready uploaded
        """
        self.create_bill()
        response = self.upload_bill()
        self.assertEqual(
            response.status_code, 
            status.HTTP_400_BAD_REQUEST)    
        self.assertDictEqual(
            response.data,
            {
                'image': [IMAGE_ALREADY_UPLOADED_ERROR]
            })    

