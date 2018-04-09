import datetime
import logging

from django.db import transaction, IntegrityError
from django.dispatch import receiver

from apps.bills import signals as bills_signals
from .models import Spending


logger = logging.getLogger(__name__)


@receiver(
    bills_signals.bill_was_created,
    dispatch_uid='create_spendings_after_bill_creation')
def create_spendings_after_bill_was_created(
        sender, bill, *args, **kwargs):
    """
    Try parse bill and create spendings
    """
    try:
        parsed_data = bill.parse_bill()
    except ValueError as e:
        logger.exception('Could not parse bill %d' % bill.id)
        return
    try:
        date = datetime.datetime.strptime(
            parsed_data['date'], '%Y-%m-%d %H:%M:%S')
        items = _aggregate_spendings_by_name(parsed_data['items'])
    except KeyError:
        logger.exception('Parsed data has wrong fromat')
        return
    for name, item in items.items():
        try:
            with transaction.atomic():
                Spending.objects.create(
                    name=name,
                    quantity=item['quantity'],
                    amount=item['amount'],
                    date=date.date(),
                    bill=bill)
        except IntegrityError:
            logger.exception(
                'Can not create item with name %s details %s' % (
                    name, item))

def _aggregate_spendings_by_name(items):
    """
    Sum quantity for spendings with same name
    """
    # Warning: we assume that items from same bill with same name
    # has also same price
    # if the prices are different information of difference will be lost
    result = {}
    for item in items:
        name = item['item'].lower()
        result[name] = result.get(
            name, 
            {
                'quantity': 0,
                'amount': 0
            })
        result[name]['quantity'] += 1
        result[name]['amount'] += item['amount']
    return result
