# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from apps.spendings.models import Spending
from apps.bills.models import Bill


class SpendingInline(admin.TabularInline):
    model = Spending


class BillAdmin(admin.ModelAdmin):
    inlines = (SpendingInline, )
    readonly_fields = ('parsed_data', )

    def parsed_data(self, bill):
        # print json of parsed bill
        # or error if bill can niot be parsed
        try:
            data = bill.parse_bill()
            return format_html_join(
               mark_safe('<pre>'),
               json.dumps(data),
               mark_safe('</pre>'),
            )
        except ValueError as e:
            error = e.args[0]
            return format_html_join(
                mark_safe('<span class="errors">'),
                error,
                mark_safe('<span>'),
            )


admin.site.register(Bill, BillAdmin)
