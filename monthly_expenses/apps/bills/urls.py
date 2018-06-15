from django.conf.urls import url

from .api import (
    UploadUniqueBillAPI,
    RetrieveUpdateBillAPI)


urlpatterns = [
    url(r'^$', UploadUniqueBillAPI.as_view(), name='bill'),
    url(
        r'^(?P<bill_id>[0-9]+)/$', 
        RetrieveUpdateBillAPI.as_view(),
        name='retrieve-update-bill')
]