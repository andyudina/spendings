from django.conf.urls import url

from .api import (
	RewriteSpending, 
	ListAggregatedByNameSpendings)


urlpatterns = [
    url(r'^$',
    	RewriteSpending.as_view(),
    	name='rewrite-spendings'),
    url(r'^name/$', 
    	ListAggregatedByNameSpendings.as_view(), 
    	name='spendings-aggregated-by-name'),
]