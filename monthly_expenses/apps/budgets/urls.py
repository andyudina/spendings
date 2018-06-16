from django.conf.urls import url

from .api import (
    ListCategories,
    ListCreateBudget,
    UpdateDeleteBudget)

# TODO: redesign urls to answer REST API standarts

urlpatterns = [
    url(r'^categories/$',
        ListCategories.as_view(),
        name='list-categories'),
    url(r'^/$',
        ListCreateBudget.as_view(),
        name='budgets'),
    url(r'^(?P<budget_id>\d+)$',
        UpdateDeleteBudget.as_view(),
        name='budget')
]