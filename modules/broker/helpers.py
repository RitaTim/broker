# -*- coding: utf-8 -*-

import os
import inspect
import importlib

from broker import MODULE_SOURCES, FILE_SOURCES


def get_db_allias_for_source(source_name):
    """
        Возварщает алиас бд источника
    """
    return "{}_source".format(source_name.lower())


def get_data_sources():
    """
        Возвращает данные по всем источникам модуля source:
            {
                <имя класса источника>: {
                    'type': <тип источника>,
                    'path': <путь к классу>
                },
                ...
            }
        Например:
            {
                'KmClient': {
                    'type': 'db',
                    'path': 'broker.sources.database.sources',
                },
                ...
            }
    """
    # Получаем текущую директорию источников
    dir_sources = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), MODULE_SOURCES
    )
    # Получаем все модули, в которых есть источники
    dirs_sources = {
        item: ".".join([__package__, MODULE_SOURCES, item, FILE_SOURCES])
        for item in os.listdir(dir_sources)
        if os.path.isdir(os.path.join(dir_sources, item))
    }

    classes_sources = {}
    for source_module, path in dirs_sources.iteritems():
        module = importlib.import_module(path)
        # Получаем список имен источников модуля, их типы и пути к классам
        classes_sources.update({
            name: {
                'type': getattr(source, 'type_source', None),
                'path': path,
            } for name, source in
            inspect.getmembers(module, predicate=inspect.isclass)
            if source.__module__ == path
        })
    return classes_sources


def get_cls_module(cls_name):
    """
        Возвращает класс модуля по имени класса cls_name
    """
    data_source = get_data_sources().get(cls_name)
    module_source = importlib.import_module(data_source['path'])
    return getattr(module_source, cls_name)
