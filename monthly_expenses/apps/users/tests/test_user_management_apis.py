"""
Test cases for user management apis
"""
from django.contrib.auth import (
    authenticate, get_user)
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status


class CreateUserAPITestCase(TestCase):
    """
    Test user creation api
    """
    def create_user(
            self, email=None, password=None):
        email = email or 'test@test.com'
        password = password or '#'
        return self.client.post(
            reverse('create-user'),
            {
                'email': email,
                'password': password
            })

    def test_user_created__successful_response_returned(self):
        """
        We return 201 created response on successful creation
        """
        response = self.create_user()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_do_not_return_password(self):
        """
        We do not return password in api response
        """
        response = self.create_user()
        self.assertNotIn(
            'password', response.data)

    def test_user_successfully_created(self):
        """
        User successfully saved in database
        with given email and password
        """
        self.create_user()
        self.assertTrue(
            # check if user can be authenticated
            # should be not None
            authenticate(
                username='test@test.com', 
                password='#'))

    def test_user_successfully_created__user_logged_in(self):
        """
        User logged in after successful creation
        """
        self.create_user()
        user = get_user(self.client)
        self.assertTrue(
            user.is_authenticated())

    def test_email_already_registered__error_returned(self):
        """
        We return 400 bad request if email was already used
        """
        prev_user = User.objects.create(
               username='test@test.com',
               email='test@test.com',
               password='#')
        response = self.create_user()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)


class LoginUserAPITest(TestCase):
    """
    Test user login API
    """
    def setUp(self):
        self.user = self.create_user()

    def create_user(
            self, email=None, password=None):
        email = email or 'test@test.com'
        password = password or '#'
        return User.objects.create_user(
            email, email, password)

    def login_user(
            self, email=None, password=None):
        email = email or 'test@test.com'
        password = password or '#'
        return self.client.post(
            reverse('login-user'),
            {
                'email': email,
                'password': password
            })

    def test_user_logged_in__successful_response_returned(self):
        """
        We return successful response if user logged in
        """
        response = self.login_user()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_do_not_return_password(self):
        """
        We do not return password in api response
        """
        response = self.login_user()
        self.assertNotIn(
            'password', response.data)

    def test_user_successfully_logged_in(self):
        """
        We log in user successfully if email and password match
        """
        self.login_user()
        user = get_user(self.client)
        self.assertTrue(
            user.is_authenticated())
        self.assertEqual(
            user, self.user)

    def test_password_doesnt_match__error_returned(self):
        """
        We return bad request error if user provided wrong password
        """
        response = self.login_user(
            password='does-not-match')
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_email_doesnt_exist__error_returned(self):
        """
        We return bad request error if email doesn't exist
        """
        response = self.login_user(
            email='does-not-exist@email.com')
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
