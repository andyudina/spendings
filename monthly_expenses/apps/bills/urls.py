from django.conf.urls import url

from .api import (
    UploadUniqueBillAPI,
    RetrieveBillAPI)


urlpatterns = [
    url(r'^$', UploadUniqueBillAPI.as_view(), name='bill'),
    url(
        r'^(?P<bill_id>[0-9]+)/$', 
        RetrieveBillAPI.as_view(), 
        name='retrieve-bill')
]