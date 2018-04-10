"""
User management api
"""
from django.contrib.auth import (
    authenticate, login)
from rest_framework import (
    serializers, 
    generics)

from django.contrib.auth.models import User


class LoginUserInSerialiserMixin(object):
    """
    Helper mixin with login logic
    Should be used only with serializer class
    """
    def login(self, data):
        user = authenticate(
            username=data['email'], 
            password=data['password'])
        login(
            self.context['request'], user)  
        return user


class UserCreateAndLoginInTheSameTimeSerializer(
        LoginUserInSerialiserMixin,
        serializers.ModelSerializer):
    """
    Serialiser to create a new user
    with unique email (which gonna be used as username)
    Logins user on creation
    """
    email = serializers.EmailField(
        write_only=True,
        required=True)
    password = serializers.CharField(
        write_only=True,
        required=True)

    def validate_email(self, email):
        if User.objects.\
                filter(email=email).\
                exists():
            raise serializers.ValidationError(
                'This email is already in use')
        return email

    def create(self, validated_data):
        User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'])
        # login user simultaneously
        user = self.login(validated_data)
        return user     

    class Meta:
        model = User
        fields = ('email', 'password')


class CreateUser(
        generics.CreateAPIView):
    """
    Create new user using given email and password
    """
    serializer_class = \
        UserCreateAndLoginInTheSameTimeSerializer


class UserLoginSerializer(
        LoginUserInSerialiserMixin,
        serializers.Serializer):
    """
    Login user using email and password
    """
    email = serializers.EmailField(
        write_only=True,
        required=True)
    password = serializers.CharField(
        write_only=True,
        required=True)

    def validate(self, data):
        # we use email instead of username
        if not authenticate(
                username=data['email'], 
                password=data['password']):
            raise serializers.ValidationError(
                'Failed to login')
        return data

    def create(self, validated_data):
        # login user instead of creation
        return self.login(validated_data)


class LoginUser(
        generics.CreateAPIView):
    """
    Login user using email and password
    """
    serializer_class = UserLoginSerializer
