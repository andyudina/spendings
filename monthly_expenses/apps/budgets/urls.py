from django.conf.urls import url

from .api import (
    ListCategories,
    CreateBudget)

# TODO: redesign urls to answer REST API standarts

urlpatterns = [
    url(r'^categories/$',
        ListCategories.as_view(),
        name='list-categories'),
    url(r'^/$',
        CreateBudget.as_view(),
        name='budgets')
]