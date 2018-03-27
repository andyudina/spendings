import os
from math import ceil
from hashlib import sha256
from PIL import Image

from django.db.models.signals import post_save
from django.dispatch import receiver

from monthly_expenses.settings import MEDIA_ROOT
from .models import Bill


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
    """

    if not created:
        # Populate hash only on creation
        return
    sha256_hash = _generate_hash_from_image(
        os.path.join(
            MEDIA_ROOT, instance.image.url))
    instance.sha256_hash_hex = sha256_hash
    instance.save(update_fields=['sha256_hash_hex'])


def _generate_hash_from_image(path):
    """
    Generate sha256 using binary contents of the image
    """
    CHUNK_SIZE = 1024
    sha256_hash = sha256()
    with open(path, 'rb') as image_binary_file:
        while(True):
            chunk = image_binary_file.read(CHUNK_SIZE)
            if not chunk: break
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest() 
