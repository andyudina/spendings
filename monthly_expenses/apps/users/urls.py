from django.conf.urls import url

from .api import (
    CreateUser, LoginUser, CurrentUser)


urlpatterns = [
    url(r'^signup/$',
        CreateUser.as_view(),
        name='create-user'),
    url(r'^login/$', 
        LoginUser.as_view(), 
        name='login-user'),
    url(r'^$',
        CurrentUser.as_view(),
        name='current-user')
]