from django.conf.urls import url

from .api import UploadBillAPI


urlpatterns = [
    url(r'^$', UploadBillAPI.as_view(), name='bill'),
]