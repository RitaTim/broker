# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .models import Source
from .helpers import get_cls_module


class SourceFunctions(View):
    """
        Вьюха для работы с методами источников
    """
    def get(self, request, type_methods, source_id):
        """
            Находит id и названия сигналов(коллбэков) класса name_source в виде
            {
                '1': 'name_signal1',
                '2': 'name_signal2',
                ...
            }
            и возвращает их в формате json
        """
        source = get_object_or_404(Source, id=source_id)
        cls = get_cls_module(source.source)
        lst_methods = cls.get_all_callbacks() if type_methods == 'callback' \
            else cls.get_all_signals()
        return HttpResponse(json.dumps({type_methods: lst_methods}))

get_source_functions = SourceFunctions.as_view()

