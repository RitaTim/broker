# -*- coding: utf-8 -*-

from broker.meta import BaseClassMeta


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
        pass
        # определяем параметры, общие для всех источников

    @staticmethod
    def get_init_params(self):
        """
            Возвращает параметры источника в формате json
        """
        pass

    @staticmethod
    def set_source_model(self, source_model):
        """
            Связывает экземпляр класса с объектом модели SourceModel
        """
        self.source_model = source_model

    @staticmethod
    def create_source_model(self):
        """
            Создает объект в таблице SourceModel
        """
        # создаем source model
        # устанавливаем атрибут self.set_source_model(source_model)
        pass


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

    # signals

    # callbacks


class IDA2(MysqlDBSource):
    """
        Класс источника IDA2
    """
    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(IDA2, self).__init__(*args, **kwargs)

    # signals

    # callbacks
