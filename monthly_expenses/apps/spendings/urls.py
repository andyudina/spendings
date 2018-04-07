from django.conf.urls import url

from .api import ListAggregatedByNameSpendings


urlpatterns = [
    url(r'^name/$', 
    	ListAggregatedByNameSpendings.as_view(), 
    	name='spendings-aggregated-by-name'),
]