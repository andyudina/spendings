"""
Rest api for budgets manipulations: create, edit, show, notify
"""
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import (
    exceptions,
    permissions,
    serializers,
    generics)

from .models import (
    Budget, Category)


class CategorySerializer(
        serializers.ModelSerializer):
    """
    Read only serialiser to display category
    """

    class Meta:
        model = Category
        fields = (
            'id', 'name')


class ListCategories(
        generics.ListAPIView):
    """
    Show all available categories 
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')


## Create and show budgets


class CreateBudgetSerializer(
        serializers.ModelSerializer):
    """
    Create budget for current user
    """
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all())
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())

    def validate(self, data):
        """
        Validate if budget for this category has not been created yet
        """
        if Budget.objects.\
                filter(
                    user=data['user'],
                    category=data['category']
                ).exists():
            raise serializers.ValdationError(
                'You\'ve already created budget for this category')
        return data

    class Meta:
        model = Budget
        fields = (
            'amount', 'user', 'category')


class CategorySerialiser(
        serializers.ModelSerializer):
    """
    Read only model serialiser to diplay category
    """
    class Meta:
        model = Category
        fields = '__all__'


class ListBudgetSerialiser(
        serializers.ModelSerializer):
    """
    Read only model serialiser to display budget
    """
    category = CategorySerialiser(read_only=True)

    class Meta:
        model = Budget
        fields = (
            'amount',
            'id',
            'category',
            'total_expenses_in_current_month',
        )


class ListCreateBudget(
        generics.ListCreateAPIView):
    """
    POST:
        Create budget for user
        - 201 CREATED: budget successfully created
        - 400: error occured

    GET:
        List all budgets for current user
        - 200 OK:
        [
            {
                'amount': [budgeting period max amount],
                'id': [budget id],
                'category': {
                    'id': [catgeory id],
                    'name': [category name],
                },
                'total_expenses_in_current_month': [total expenses amount]
            }
        ]
    """
    permission_classes = (
        permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateBudgetSerializer
        elif self.request.method == 'GET':
            return ListBudgetSerialiser
        raise exceptions.MethodNotAllowed(self.request.method)

    def get_queryset(self):
        """
        On get request this view returns a list of all budgets
        for the currently authenticated user.
        """
        user = self.request.user
        return Budget.objects.filter(user=user)
