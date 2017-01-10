# -*- coding: utf-8 -*-

from django.conf import settings

from broker.decorators.decorators import signal, callback
from broker.meta import BaseClassMeta

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
        cls_name = self.__class__.__name__
        try:
            self.source_model = SourceModel.objects.get(source=cls_name)
        except SourceModel.DoesNotExist:
            raise ValueError(u"Source '{}' not has object of model"
                             .format(cls_name))


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    type_source = u"db"

    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД

    def get_alias_db(self):
        """
            Возварщает алиас бд источника
        """
        return "{}_source".format(self.source_model.source.lower())

    def get_connection_cursor(self):
        """
            Возвращает коннектор к базе данных
        """
        return settings.CONNECTIONS_SOURCES[self.get_alias_db()].cursor()


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    def __init__(self, *args, **kwargs):
        super(MysqlDBSource, self).__init__(*args, **kwargs)
        # определяем параметры источника - mysql БД


""" Инстансы источников """


class Wsdl(Source):
    """
        Класс источника Wsdl
    """
    type_source = u"wsdl"

    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(Wsdl, self).__init__(*args, **kwargs)


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
    def km_callback_1(self, *args, **kwargs):
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
    def ida_callback_1(self, *args, **kwargs):
        # Работать с бд источника можно через ее коннектор
        cursor = self.get_connection_cursor()
        cursor.execute("SELECT * FROM test")
        print(cursor.fetchall())

        import random
        fortuna = random.randint(0, 100)
        print 'ida_callback_1 - {0}'.format(fortuna)
        if fortuna <= 60:
            raise SpecialException('ha ha ha HA')
        return 'All is well!'

    @callback
    def ida_callback_2(self, *args, **kwargs):
        print 'ida_callback_2'


class SpecialException(Exception):
    pass
