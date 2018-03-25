# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


SHA256_LEN_HEX = 64


class Bill(models.Model):
    """
    Stores image of the bill.
    Responsible for parcing the image
    """
    image = models.ImageField(
        upload_to='media/',
        blank=False,
        null=False)
    # Is populated by post_save signal
    sha256_hash_hex = models.CharField(
        max_length=SHA256_LEN_HEX,
        unique=True,
        blank=True,
        null=True)
    create_time = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False)
    # Text information from bill
    # Saved as dumped json
    parced_data = models.TextField()





