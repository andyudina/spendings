# -*- coding: utf-8 -*-
from PIL import Image

from django.db import models
from pytesseract import image_to_string


SHA256_LEN_HEX = 64


class Bill(models.Model):
    """
    Stores image of the bill.
    Responsible for parcing the image
    """
    # TODO: set image widthand height requirements so 
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


    def parse_bill(self, reparse=False):
        """
        Get text information from bill image and
        extract datet ime of the bill, spendings types and amounts
        """
        import json
        if not reparse and self.parsed_data:
            return self.parcsd_data
        bill_text = self._get_text_from_image()
        self.parsed_data = json.dumps(
            self._get_datetime_and_spendings_from_bill(bill_text))
        self.save(update_fields=['parsed_data'])
        return self.parsed_data

    def _get_text_from_image(self):
        """
        Extract text from inmage with OCR
        """
        import os
        from monthly_expenses.settings import MEDIA_ROOT
        image_path = os.path.join(MEDIA_ROOT, self.image.url)
        image = Image.open(image_path)
        return image_to_string(image)

    def _get_datetime_and_spendings_from_bill(self, bill_text):
        """
        Get datetime when bill was created and information about spendings:
        type, amount
     
        WARNING: parsing implementation is not robust and covers only
        limited amount of bills formats (for MVP)
        TODO: use NNs to extract bill information
        """
        bill_by_lines = [
            line.strip() for line in bill_text.splitlines()
            if line.strip()]
        bill_by_words = [
            word.strip() for word in bill_text.split()]
        return {
            'date': self._find_date(bill_by_words),
            'items': self._find_items(bill_by_lines)
        }

    def _find_date(self, bill_words):
        """
        Find date of the bill
        """
        from dateutil import parser
        # WARING: 4 sumbols dates without stop symbols can not be used here
        MIN_WORD_LENGTH = 6 # 2 - year, 1 - month, 1 - day, 2 - stop symbols
        for word in bill_words:
            if len(word) < MIN_WORD_LENGTH:
                continue
            try:
                date = parser.parse(word)
                return str(date)
            # not date - ok to skip
            except ValueError:
                pass
            except OverflowError:
                pass
        raise ValueError('No date found')

    def _find_items(self, bill_lines):
        """
        Find items of the bill
        """
        items = []
        for line in bill_lines:
            # don't proceed further that total sum line
            if self._is_total_line(line):
                break
            # try to pass each line
            # like it has bought item
            try:
                item = self._get_item_from_line(line)
                items.append(item)
            except ValueError:
                pass
        if not items:
            raise ValueError('No items found')
        return items

    def _is_total_line(self, line):
        """
        Check if line has total anount of the check
        """
        return 'total' in line.lower()

    def _get_item_from_line(self, line):
        """
        Try to parse item from bill line.
        Raise ValueError if no item found
        """
        import re
        match = re.search('^([a-zA-Z\s]+)([\d]+)', line)
        if not match:
            raise ValueError('No item found')
        # Currently only one currency is supported (EUR)
        item = match.group(1).strip()
        quantity = int(match.group(2))
        # Find amount in last part of line
        # Assume that it's the last value in line
        amount = None
        line_by_words = line.split()
        for word in line_by_words[::-1]:
            try:
                amount = float(word.replace(',', '.'))
                break
            except ValueError:
                pass
        if amount is None:
            raise ValueError('Amount not found for item')
        return {
            'item': item,
            'quantity': quantity,
            'amount': amount
        }
