from django.conf.urls import url

from .api import UploadUniqueBillAPI


urlpatterns = [
    url(r'^$', UploadUniqueBillAPI.as_view(), name='bill'),
]