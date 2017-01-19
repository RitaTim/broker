# -*- coding: utf-8 -*-
"""
    Данный модуль содержит базовые классы для работы со всеми типами источников

    Сами источники необходимо добавлять в файл с именем sources.py
    в модуль конкретного типа источника
    Примечание:
        при смене имени файла sources, поменять значение broker.FILE_SOURCES
"""
from broker.meta import BaseClassMeta
from broker.models import Source as SourceModel


class BaseClass(object):
    """
        Базовый класс
    """
    __metaclass__ = BaseClassMeta


class Source(BaseClass):
    """
        Базовый класс для всех источников
    """
    type_source = None
    source_model = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__()
        cls_name = self.__class__.__name__
        try:
            self.source_model = SourceModel.objects.get(source=cls_name)
        except SourceModel.DoesNotExist:
            raise ValueError("Source '{}' not has object of model"
                             .format(cls_name))


class TransactionAtomicManager(object):
    """
        Отключает autocommit на время выполнения функции и
        откатывает изменения в случае ошибки
    """
    def __init__(self, connector, *args, **kwargs):
        super(TransactionAtomicManager, self).__init__()
        self.connector = connector
        self.autocommit = self.connector.get_autocommit()

    def __enter__(self, *args, **kwargs):
        if self.autocommit:
            self.connector.set_autocommit(False)

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            self.connector.commit()
        else:
            # В случае ошибки, откатываем изменения
            self.connector.rollback()

        if self.autocommit:
            self.connector.set_autocommit(True)
