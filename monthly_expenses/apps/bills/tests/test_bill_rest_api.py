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


class UploadBillRestAPITest(BillTestCase):
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


class RetrieveBillRestAPITest(BillTestCase):
    """
    Test rest api endpoint for retrieving bills
    """
    def setUp(self):
        self.user = self.get_or_create_user()
        self.bill = self.create_bill()

    def retrieve_bill(
            self, 
            bill_id=None, 
            auth_needed=True):
        """
        Helper to retrieve bill via api
        """
        bill_id = bill_id or self.bill.id
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.get(
            reverse(
                'retrieve-update-bill', 
                kwargs={
                    'bill_id': bill_id
                }))

    def test_retrieve_bill__successfull_response(self):
        """
        We return 200 OK when bill is successfully retrieved
        """
        response = self.retrieve_bill()
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)

    def test_retrieve_bill__bill_and_categories_returned(self):
        """
        We return basic bill info and all linked categories
        """
        self.create_categories_for_bill(self.bill)
        response = self.retrieve_bill()
        self.assertDictEqual(
            response.data,
            {
                'image': self.bill.image.url,
                'date': self.bill.date,
                'categories': [
                    {
                        'category': {
                           'name': 'a-test',
                           'id': 1,
                        },
                        'id': 1,
                        'amount': 10
                    },
                    {
                        'category': {
                            'name': 'b-test',
                            'id': 2
                        },
                        'id': 2,
                        'amount': 20
                    },
                ]
            })

    def test_retrieve_bill_without_auth__error_returned(self):
        """
        We return 403 forbidden if user is not logged in
        """   
        response = self.retrieve_bill(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_retrieve_bill_for_another_user__error_returned(self):
        """
        We return 403 forbidden if user tries to retrieve bill
        created by another user
        """
        new_user = self.get_or_create_user(
            email='new-test-1@test.com')
        self.bill.user = new_user
        self.bill.save(update_fields=['user', ])
        response = self.retrieve_bill()
        self.assertEqual(
            response.status_code, 
            status.HTTP_403_FORBIDDEN)

    def test_retrieve_non_existing_bill___error_returned(self):
        """
        We return 404 not found if user tries to retrieve bill
        with invalid id
        """   
        response = self.retrieve_bill(bill_id=self.bill.id + 1)
        self.assertEqual(
            response.status_code, 
            status.HTTP_404_NOT_FOUND)


class UpdateBillRestAPITest(BillTestCase):
    """
    Test rest api endpoint for updating bill categories
    """
    def setUp(self):
        self.user = self.get_or_create_user()
        self.bill = self.create_bill()

    def update_bill(
            self,
            data=None,
            bill_id=None, 
            auth_needed=True):
        """
        Helper to retrieve bill via api
        """
        import json
        data = data or {
            'categories': []
        }
        bill_id = bill_id or self.bill.id
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.patch(
            reverse(
                'retrieve-update-bill',
                kwargs={
                    'bill_id': bill_id
                }),
            json.dumps(data),
            content_type='application/json')

    def test_update_bill__successfull_response(self):
        """
        We return 200 OK when bill is successfully updated
        """
        response = self.update_bill()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_add_new_category_to_bill__categories_updated(self):
        """
        We successfully add new category to bill
        """
        from apps.budgets.models import Category
        self.create_categories_for_bill(self.bill)
        category = Category.objects.create(name='d-test')
        response = self.update_bill(
            data={
            'categories': [
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
                {
                    'category': {
                        'id': category.id,
                        'name': 'd-test'
                    },
                    'amount': 30
                },
            ]})
        self.assertTrue(
            self.bill.categories.\
                filter(id=category.id).exists())

    def test_delete_category_to_bill__categories_updated(self):
        """
        We successfully remove category from bill
        """
        self.create_categories_for_bill(self.bill)
        response = self.update_bill(
            data={
            'categories': [
                {
                    'category': {
                        'id': 1,
                        'name': 'a-test'
                    },
                   'id': 1,
                    'amount': 10
                }
            ]})
        self.assertFalse(
            self.bill.categories.\
                filter(name='b-test').exists())

    def test_edit_category_amount__categories_updated(self):
        """
        We successfully edit category amount
        """
        self.create_categories_for_bill(self.bill)
        response = self.update_bill(
            data={
            'categories': [
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
                    'amount': 30
                },
            ]})
        self.assertTrue(
            self.bill.categories.\
                filter(
                    name='b-test',
                    category_to_bill__amount=30.0).exists())

    def test_add_non_existing_category__400_returned(self):
        """
        We return 400 bad request if category doesn't exist
        """
        self.create_categories_for_bill(self.bill)
        response = self.update_bill(
            data={
            'categories': [
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
                {
                    'category': {
                        'id': 3,
                        'name': 'd-test'
                    },
                    'amount': 30
                },
            ]})
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_add_non_existing_category__new_category_wasnt_created(self):
        """
        We do not create new category if category doesn't exist
        """
        from apps.budgets.models import Category
        self.create_categories_for_bill(self.bill)
        response = self.update_bill(
            data={
            'categories': [
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
                {
                    'category': {
                        'id': 3,
                        'name': 'd-test'
                    },
                    'amount': 30
                },
            ]})
        self.assertFalse(
            Category.objects.filter(name='d-test').exists())

    def test_update_bill_without_auth__error_returned(self):
        """
        We return 403 forbidden if user is not logged in
        """
        response = self.update_bill(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_update_bill_for_another_user__error_returned(self):
        """
        We return 403 forbidden if user tries to update bill
        created by another user
        """
        new_user = self.get_or_create_user(
            email='new-test-1@test.com')
        self.bill.user = new_user
        self.bill.save(update_fields=['user', ])
        response = self.update_bill()
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_update_non_existing_bill___error_returned(self):
        """
        We return 404 not found if user tries to update bill
        with invalid id
        """
        response = self.update_bill(bill_id=self.bill.id + 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)


class ListBillRestAPITest(BillTestCase):
    """
    Test rest api endpoints for listing bills
    """
    def setUp(self):
        self.user = self.get_or_create_user()
        self.bill = self.create_bill()

    def list_bills(
            self, auth_needed=True):
        """
        Helper to upload bill via api
        """
        if auth_needed:
            self.client.force_login(self.user)
        return self.client.get(
            reverse('bill'))

    def test_list_bill__successfull_response(self):
        """
        We return 200 when bills are successfully listed
        """
        response = self.list_bills()
        self.assertEqual(
            response.status_code, 
            status.HTTP_200_OK)

    def test_list_bill__valid_information_returned(self):
        """
        We return valid information about bill
        """
        response = self.list_bills()
        self.assertListEqual(
            response.data,
            [
                {
                    'id': self.bill.id,
                    'image': self.bill.image.url,
                    'has_categories': False
                }
            ]
        )

    def test_list_bill_with_categories(self):
        """
        We return flag that showes if bill has categories
        """
        self.create_categories_for_bill(self.bill)
        response = self.list_bills()
        self.assertTrue(
            response.data[0]['has_categories'])

    def test_list_bill__filter_out_bills_for_different_user(self):
        """
        We show only bills for current user
        """
        new_user = self.get_or_create_user(
            email='new-test-1@test.com')
        self.bill.user = new_user
        self.bill.save(update_fields=['user', ])
        response = self.list_bills()
        self.assertListEqual(
            response.data, [])

    def test_not_authenticated_tries_to_list_bills__error_returned(self):
        """
        We return 403 forbidden if user is not logged in
        """
        response = self.list_bills(
            auth_needed=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
