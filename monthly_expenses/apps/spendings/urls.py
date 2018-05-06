from django.conf.urls import url

from .api import (
    ListOrRewriteSpending, 
    ListMostExpensiveSpendings,
    ListMostPopularSpendings)

# TODO: redesign urls to answer REST API standarts

urlpatterns = [
    url(r'^(?P<bill_id>[0-9]+)/$',
        ListOrRewriteSpending.as_view(),
        name='rewrite-list-spendings'),
    url(r'^expensive/$', 
        ListMostExpensiveSpendings.as_view(), 
        name='spendings-aggregated-by-name-sorted-by-amount'),
    url(r'^popular/$', 
        ListMostPopularSpendings.as_view(), 
        name='spendings-aggregated-by-name-sorted-by-quantity'),
]