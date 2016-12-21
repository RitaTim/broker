# -*- coding: utf-8 -*-

from django.conf.urls import url

from broker.views import get_source_functions

urlpatterns = [
    url(
        r'^source/get_methods/(?P<type_methods>\w+)/(?P<source_id>\w+)/$',
        get_source_functions,
        name='get_source_functions'
    ),
]
