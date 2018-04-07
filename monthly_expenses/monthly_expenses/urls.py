from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/bills/', include('apps.bills.urls')),
    url(r'^api/spendings/', include('apps.spendings.urls')),
]