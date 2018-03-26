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
    # tesseract can recognize the image
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
        if not reparse and self.parsed_data:
            return self.parcsd_data
        bill_text = self._get_text_from_image()
        self.parsed_data = self._get_datetime_and_spendings_from_bill(bill_text)
        self.save(update_fields=['parsed_data'])
        return self.parsed_data

    def _get_text_from_image(self):
        """
        Extract text from inmage with OCR
        """
        import os
        from monthly_expenses.settings import BASE_DIR
        image_path = os.path.join(BASE_DIR, self.image.url)
        image = Image.open(image_path)
        return image_to_string(image)

    def _get_datetime_and_spendings_from_bill(self, bill_text):
        """
        STUB. Get datetime when bill was created and information about spendings:
        type, amount
        """
        return bill_text
