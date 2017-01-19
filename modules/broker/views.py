# -*- coding: utf-8 -*-

import json
import importlib

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .models import Source
from .helpers import get_data_sources


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
        module_sources = get_data_sources()
        module = importlib.import_module(module_sources[source.source]['path'])
        cls = getattr(module, source.source)
        lst_methods = cls.all_callbacks if type_methods == 'callback' \
            else cls.all_signals
        func_names = [f.func_name for f in lst_methods]
        return HttpResponse(json.dumps({type_methods: func_names}))

get_source_functions = SourceFunctions.as_view()

