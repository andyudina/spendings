from django.dispatch import Signal

bill_was_created = Signal(
    providing_args=['bill'])