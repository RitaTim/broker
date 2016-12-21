# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .models import Source


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
        module = __import__('broker')
        source = get_object_or_404(Source, id=source_id)
        cls = getattr(module.sources, source.source)
        lst_methods = cls.all_callbacks if type_methods == 'callbacks' \
            else cls.all_signals
        func_names = [f.func_name for f in lst_methods]
        return HttpResponse(json.dumps({type_methods: func_names}))

get_source_functions = SourceFunctions.as_view()

