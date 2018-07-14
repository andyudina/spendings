"""
User management api
"""
from django.contrib.auth import (
    authenticate, login)
from django.http import Http404
from rest_framework import (
    response,
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


class UserSerializer(
        serializers.ModelSerializer):
    """
    Read only user serialzer
    """
    class Meta:
        model = User
        fields = ('email', )


class CurrentUser(
        generics.RetrieveAPIView):
    """
    Retrieve user info if user is logged in
    Returns user info if user is logged in
    or raises 404
    """
    serializer_class = UserSerializer

    def get_object(self):
        """
        Returns current user or raises 404
        """
        if self.request.user.is_authenticated():
            return self.request.user
        raise Http404


class UserWithBudgetSerializer(
        serializers.ModelSerializer):
    """
    Read only user serialzer with total budget
    """
    total_budget = serializers.SerializerMethodField()
    total_spent_budget = serializers.SerializerMethodField()

    def get_total_budget(self, obj):
        return obj.total_budget.amount

    def get_total_spent_budget(self, obj):
        return obj.total_budget.total_expenses_in_current_month

    class Meta:
        model = User
        fields = (
            'id', 'total_budget',
            'total_spent_budget')


class SignupAnonymousUser(
        generics.GenericAPIView):
    """
    Create anonymous user and log in as newly created user
    """
    serializer_class = UserWithBudgetSerializer

    def _create_anonymous_user(self):
        """
        Generate unique hash for username
        Create anon user using hash
        """
        import uuid
        username = uuid.uuid4().hex
        random_password = uuid.uuid4().hex
        return User.objects.create_user(
            username=username,
            email='%s@anon.anon' % username,
            password=random_password)

    def _get_user_data(self, user):
        """
        Serialize and return in response user data
        """
        serializer = self.get_serializer(user)
        return response.Response(serializer.data)

    def post(
            self, request, *args, **kwargs):
        if request.user.is_authenticated():
            # do not create new user
            # for already logged in customer
            return self._get_user_data(request.user)
        user = self._create_anonymous_user()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return self._get_user_data(request.user)
