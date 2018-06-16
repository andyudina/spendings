"""
Rest api for budgets manipulations: create, edit, show, notify
"""
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import (
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


class CreateBudget(
        generics.CreateAPIView):
    """
    Create budget for user
    """
    serializer_class = CreateBudgetSerializer
    permission_classes = (
        permissions.IsAuthenticated, )
