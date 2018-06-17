from django.conf.urls import url

from .api import (
    CreateUser, LoginUser, CurrentUser,
    SignupAnonymousUser)


urlpatterns = [
    url(r'^signup/$',
        CreateUser.as_view(),
        name='create-user'),
    url(r'^login/$', 
        LoginUser.as_view(), 
        name='login-user'),
    url(r'^$',
        CurrentUser.as_view(),
        name='current-user'),
    url(r'^anonymous/$',
        SignupAnonymousUser.as_view(),
        name='create-anon-user')
]