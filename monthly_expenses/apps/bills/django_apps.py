# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class BillsConfig(AppConfig):
    name = 'apps.bills'

    def ready(self):
        import handlers