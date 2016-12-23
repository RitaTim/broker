# -*- coding: utf-8 -*-

from broker.meta import BaseClassMeta

from decorators import signal, callback
from .models import Source as SourceModel


class BaseClass(object):
    """
        Базовый класс
    """
    __metaclass__ = BaseClassMeta

    # По умолчанию, класс является промежуточным звеном между инстансом и
    # базовым классом. В классе реального источника, нужно установить False
    is_proxy = True


class Source(BaseClass):
    """
        Базовый класс для всех источников
    """
    type_source = None
    source_model = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__()
        # определяем параметры, общие для всех источников

    def get_source_model(self):
        """
            Возвращает объект модели Source по имени класса
        """
        if SourceModel.objects.filter(source=self.__class__.__name__).exists():
            return SourceModel.objects.get(source=self.__class__.__name__)
        return None


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД

    # signals

    # callbacks


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    def __init__(self, *args, **kwargs):
        super(MysqlDBSource, self).__init__(*args, **kwargs)
        # определяем параметры источника - mysql БД


""" Инстансы источников """


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(KmClient, self).__init__(*args, **kwargs)

    @signal()
    def km_signal_1(self):
        pass

    @signal()
    def km_signal_2(self):
        pass

    def km_signal_3(self):
        pass

    @callback
    def km_callback_1(self):
        pass


class IDA2(MysqlDBSource):
    """
        Класс источника IDA2
    """
    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(IDA2, self).__init__(*args, **kwargs)

    @signal()
    def ida_signal_1(self):
        pass

    def ida_signal_2(self):
        pass

    @callback
    def ida_callback_1(self):
        pass

    @callback
    def ida_callback_2(self):
        pass
