# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class SpendingsConfig(AppConfig):
    name = 'apps.spendings'

    def ready(self):
        import handlers  