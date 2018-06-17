# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    """
    Store budget period category
    """
    name = models.CharField(
        verbose_name='Name',
        max_length=255)

    def __str__(self):
        return self.name


class BillCategory(models.Model):
    """
    Store categorised amount for bill
    """
    bill = models.ForeignKey(
        'bills.Bill',
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='bill_to_category')
    category = models.ForeignKey(
        Category,
        null=False, blank=False,
        on_delete=models.CASCADE,
        related_name='category_to_bill')
    amount = models.FloatField(null=False, blank=False)

    def __str__(self):
        return '%s for %s' % (
            self.category,
            self.bill)

    class Meta:
        unique_together = (
            ('bill', 'category'),
        )


class Budget(models.Model):
    """
    Store categorised budget for user
    """
    category = models.ForeignKey(
        Category,
        null=False, blank=False)
    user = models.ForeignKey(
        'auth.User',
        blank=False, null=False,
        related_name='categorised_budgets')
    amount = models.FloatField(
        null=False, blank=False)

    def __str__(self):
        return 'Budget %s for %s' % (
            self.category,
            self.user)

    @property
    def total_expenses_in_current_month(self):
        """
        Calculate total expenses in current month
        """
        # TODO: better accept date ranges in api
        # that will aloow apis to be more persistent and flexible
        today = datetime.date.today()
        begin_of_the_month = today.replace(day=1)
        return self.calculate_total_expenses(
            begin_date=begin_of_the_month)

    def calculate_total_expenses(
            self, begin_date=None, end_date=None):
        """
        Calculate total expenses for budgeting category
        in given time frame
        """
        # TODO: we do not support uploading bill
        # not in the same day as purchase
        qs = BillCategory.objects.filter(
            category=self.category,
            bill__user=self.user)
        if begin_date:
            qs = qs.filter(
                bill__create_time__gte=begin_date)
        if end_date:
            qs = qs.filter(
                bill__create_time__lt=end_date)
        return qs.aggregate(models.Sum('amount'))['amount__sum'] or 0

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Budget, self).save(*args, **kwargs)

    def clean(self):
        """
        Validate that total budget is equal or more than sum of
        categorised budgets
        """
        if self.user.total_budget.amount < \
            (
                self.user.categorised_budgets.\
                exclude(id=self.id).\
                aggregate(models.Sum('amount'))\
               ['amount__sum'] or 0
            ) + self.amount:
            raise ValidationError(
                'total budget amount can not be less than sum of categorised '
                'budgets amounts')

    class Meta:
        unique_together = (
            ('user', 'category'),
        )


class TotalBudget(models.Model):
    """
    Stores total budget for a user, regardless categories
    Total budget can be more or equal to sum of categorised budgets
    """
    user = models.OneToOneField(
        'auth.User',
        blank=False, null=False,
        related_name='total_budget')
    amount = models.FloatField(
        null=False, blank=False)

    def __str__(self):
        return 'Total budget for %s' % (
            self.user)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(TotalBudget, self).save(*args, **kwargs)

    def clean(self):
        """
        Validate that total budget is equal or more than sum of
        categorised budgets
        """
        if self.amount < \
            (
                self.user.categorised_budgets.\
                aggregate(models.Sum('amount'))\
               ['amount__sum'] or 0
            ):
            raise ValidationError(
                'total budget amount can not be less than sum of categorised '
                'budgets amounts')
