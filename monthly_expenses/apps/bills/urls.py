from django.conf.urls import url

from .api import (
    ListUploadUniqueBillAPI,
    RetrieveUpdateBillAPI)


urlpatterns = [
    url(r'^$', ListUploadUniqueBillAPI.as_view(), name='bill'),
    url(
        r'^(?P<bill_id>[0-9]+)/$', 
        RetrieveUpdateBillAPI.as_view(),
        name='retrieve-update-bill')
]