# -*- coding: utf-8 -*-
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
        blank=False, null=False)
    amount = models.FloatField(
        null=False, blank=False)

    def __str__(self):
        return 'Budget %s for %s' % (
            self.category,
            self.user)

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

    class Meta:
        unique_together = (
            ('user', 'category'),
        )

