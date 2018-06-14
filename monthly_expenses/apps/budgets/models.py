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