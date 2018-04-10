from django.conf.urls import url

from .api import (
    CreateUser, LoginUser)


urlpatterns = [
    url(r'^$',
        CreateUser.as_view(),
        name='create-user'),
    url(r'^login/$', 
        LoginUser.as_view(), 
        name='login-user'),
]