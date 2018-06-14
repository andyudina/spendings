"""
Rest api for budgets manipulations: create, edit, show, notify
"""
from django.db import transaction
from rest_framework import (
    serializers,
    generics)

from .models import Category


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
