# -*- coding: utf-8 -*-
import logging
from PIL import Image

from django.conf import settings
from django.db import models, transaction
from pytesseract import image_to_string

from .parsers import load_parser


logger = logging.getLogger(__name__)
# currently only one parser is supported
parser = load_parser(settings.PARSER)
SHA256_LEN_HEX = 64


class Bill(models.Model):
    """
    Stores image of the bill.
    Responsible for parcing the image
    """
    # TODO: set image width and height requirements so
    # we can avoid too small and unparsable images
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
    parsed_data = models.TextField()
    # Purchase date on the bill
    date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(
        'auth.User', blank=False, null=False,
        verbose_name='Owner')
    categories = models.ManyToManyField(
        'budgets.Category',
        through='budgets.BillCategory')

    @property
    def has_categories(self):
        return self.categories.all().exists()

    def parse_bill(self, reparse=False):
        """
        Get text information from bill image and
        extract datet ime of the bill, spendings types and amounts

        Raises ValueError in case bill can not be parsed
        """
        import json
        if not reparse and self.parsed_data:
            return json.loads(self.parsed_data)
        try:
            bill_text = self._get_text_from_image()
        except IOError:
            logger.exception('File not found')
            raise ValueError('File not found')
        parsed_data = \
            parser.get_datetime_and_spendings_from_bill(bill_text)
        self.parsed_data = json.dumps(parsed_data)
        self.save(update_fields=['parsed_data'])
        return parsed_data

    def _get_text_from_image(self):
        """
        Extract text from inmage with OCR
        """
        import os
        from monthly_expenses.settings import MEDIA_ROOT
        image_path = os.path.join(MEDIA_ROOT, self.image.url)
        image = Image.open(image_path)
        return image_to_string(image)

    def create_categories_in_bulk(self, categories):
        """
        Accepts list of dictionaries with format:
        [
            {
                'id': [category to bill id -- optional],
                'amount': [amount of category in bill],
                'category': {
                    'id': [category id],
                    'name': [category name -- optional]
                }
            }
        ]
        Creates in bulk bill to categories links
        No format validation is performed
        """
        from apps.budgets.models import (
            Category, BillCategory)
        categories_to_be_created = [
           BillCategory(
                amount=category['amount'],
                category=Category.objects.get(
                    # TODO: shitty solution from performance prospective
                    # For now it's better fail loudly here
                    id=category['category']['id']),
                bill=self
            )
           for category in categories
        ]
        with transaction.atomic():
            BillCategory.objects.bulk_create(
                categories_to_be_created)
