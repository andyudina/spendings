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