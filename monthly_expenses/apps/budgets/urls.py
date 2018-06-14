from django.conf.urls import url

from .api import (
    ListCategories)

# TODO: redesign urls to answer REST API standarts

urlpatterns = [
    url(r'^categories/$',
        ListCategories.as_view(),
        name='list-categories'),
]