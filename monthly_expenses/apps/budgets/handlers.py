from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TotalBudget


@receiver(
    post_save, 
    sender=User,
    dispatch_uid='user.create_total_budget')
def create_total_budget(
        sender, instance, created,
        *args, **kwargs):
    """
    Create empty total budget for newly created user
    """
    if not created:
        return
    budget, created = TotalBudget.objects.get_or_create(
        user=instance,
        defaults={
            'amount': 0
        })