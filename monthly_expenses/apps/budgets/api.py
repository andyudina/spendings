"""
Rest api for budgets manipulations: create, edit, show, notify
"""
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import (
    mixins,
    exceptions,
    permissions,
    serializers,
    generics)

from apps.users.permissions import IsOwner
from .models import (
    TotalBudget, Budget, Category)


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
        queryset=User.objects.all(),
        write_only=True)
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
            'amount', 'user', 'category', 'id')


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


## Update and delete budgets


class UpdateBudgetSerialiser(
        serializers.ModelSerializer):
    """
    Update budget amount
    """

    class Meta:
        model = Budget
        fields = ('amount', )


class UpdateDeleteBudget(
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        generics.GenericAPIView):
    """
    DELETE:
        Delete budget
        - 204 DELETED: budget was successfully deleted

    PATCH:
        Update budget amount
        - 200 OK: budget was successfully updated
    """
    lookup_url_kwarg = 'budget_id'
    serializer_class = UpdateBudgetSerialiser
    queryset = Budget.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TotalBudgetSerialiser(
        serializers.ModelSerializer):
    """
    Serialiser to retrieve and update
    total budet amount
    """
    class Meta:
        model = TotalBudget
        fields = ('amount', )


class RetrieveUpdateTotalBudget(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        generics.GenericAPIView):
    """
    GET:
        Retrieve total budget amount for current user
        - 200 OK:
        {
            'amount': [total budget amount]
        }
    PATCH:
        Update total budget amount for current user
        - 200 OK: amount updated
        - 400 BAD REQUEST: error occured
    """
    serializer_class = TotalBudgetSerialiser
    permission_classes = (
        permissions.IsAuthenticated, )

    def get_object(self):
        # expects total budget to be already created
        # for authenticated user
        return self.request.user.total_budget

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
