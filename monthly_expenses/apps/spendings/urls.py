from django.conf.urls import url

from .api import (
    RewriteSpending, 
    ListMostExpensiveSpendings,
    ListMostPopularSpendings)

# TODO: redesign urls to answer REST API standarts

urlpatterns = [
    url(r'^$',
        RewriteSpending.as_view(),
        name='rewrite-spendings'),
    url(r'^expensive/$', 
        ListMostExpensiveSpendings.as_view(), 
        name='spendings-aggregated-by-name-sorted-by-amount'),
    url(r'^popular/$', 
        ListMostPopularSpendings.as_view(), 
        name='spendings-aggregated-by-name-sorted-by-quantity'),
]