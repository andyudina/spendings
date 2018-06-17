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


class GetCurrentUserAPITest(TestCase):
    """
    Test api to retrieve current user
    """
    def setUp(self):
        self.user = self.create_user()

    def create_user(self):
        email = 'test@test.com'
        password = '#'
        return User.objects.create_user(
            email, email, password)

    def get_user(
            self, is_logged_in=True):
        if is_logged_in:
            self.client.force_login(self.user)
        return self.client.get(
            reverse('current-user'))

    def test_user_logged_in__successful_response_returned(self):
        """
        We return successful response if user logged in
        """
        response = self.get_user()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_user_logged_in__user_email_returned(self):
        """
        We return successful response if user logged in
        """
        response = self.get_user()
        self.assertEqual(
            response.data,
            {
                'email': 'test@test.com'
            })

    def test_user_not_logged_in__404_returned(self):
        """
        We raise 404 if user is not logged in
        """
        response = self.get_user(is_logged_in=False)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)


class SignupAnonymousUserTestCase(TestCase):
    """
    Test api for creating and loging in anonymous users
    """

    def create_user(self):
        return self.client.post(
            reverse('create-anon-user'))

    def test_ok_response_returned(self):
        """
        We return 200 OK response if user
        was created successfullt
        """
        response = self.create_user()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_new_user_created(self):
        """
        We create new anonymous user on successful request
        """
        self.assertEqual(
            User.objects.count(), 0)
        self.create_user()
        self.assertEqual(
            User.objects.count(), 1)

    def test_user_logged_in(self):
        """
        We log in newly created anonymous user
        """
        response = self.create_user()
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_already_logged_in__new_user_was_not_created(self):
        """
        We do not create new user for already logged in user
        """
        # create and log in user
        user = User.objects.create_user(
            'test@test.com', 
            'test@test.com', '#')
        self.client.force_login(user)
        # try create user once again
        response = self.create_user()
        loggedin_user = get_user(self.client)
        # make sure user is still logged in as previous user
        self.assertEqual(
            user, loggedin_user)
        # make sure new user is not created
        self.assertFalse(
            User.objects.exclude(id=user.id).exists())
