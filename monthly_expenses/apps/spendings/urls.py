from django.conf.urls import url

from .api import (
	CreateSpending, 
	ListAggregatedByNameSpendings)


urlpatterns = [
    url(r'^$',
    	CreateSpending.as_view(),
    	name='create-spendings'),
    url(r'^name/$', 
    	ListAggregatedByNameSpendings.as_view(), 
    	name='spendings-aggregated-by-name'),
]