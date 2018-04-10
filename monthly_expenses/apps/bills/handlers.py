import logging
import os

from math import ceil
from PIL import Image

from django.db.models.signals import (
    post_save, post_delete)
from django.dispatch import receiver

from monthly_expenses.settings import MEDIA_ROOT
from .models import Bill
from .utils import generate_hash_from_image


logger = logging.getLogger(__name__)


@receiver(
    post_save, 
    sender=Bill,
    dispatch_uid='bill.populate_hash')
def populate_bill_hash(
        sender, instance, created,
        *args, **kwargs):
    """
    Generate sha256 hash for given image and populate
    hash field of sender instance with it
    Can rise IntegrityError
    """

    if not created:
        # Populate hash only on creation
        return
    image_file_path = os.path.join(
            MEDIA_ROOT, instance.image.url)
    with open(image_file_path, 'rb') as image_binary_file:
        sha256_hash = \
            generate_hash_from_image(image_binary_file)
    instance.sha256_hash_hex = sha256_hash
    # can raise IntegrityError here
    instance.save(update_fields=['sha256_hash_hex'])


@receiver(
    post_delete, 
    sender=Bill,
    dispatch_uid='bill.remove_image_file')
def remove_image_file(
        sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding Bill object is deleted
    """
    if not instance.image:
        logger.debug(
            'No image found for bill %d' % bill.id)
        return
    if not os.path.isfile(instance.image.path):
        logger.error(
            'Bill image seems to be not a file %d' % bill.id)
        return
    logger.debug(
        'Deleting image with path %s' % instance.image.path)
    os.remove(instance.image.path)
