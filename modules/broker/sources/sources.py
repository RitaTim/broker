# -*- coding: utf-8 -*-

from broker.decorators.decorators import signal, callback
from broker.sources.proxy import DataBaseSourse, Source
from broker.sources.sql import MysqlQuery
from broker.sources.connections import MysqlConnect, PostgresConnect


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    def __init__(self, *args, **kwargs):
        super(MysqlDBSource, self).__init__(*args, **kwargs)

    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд MySQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return MysqlConnect(**params)


class PostgresSQL(DataBaseSourse):
    """
        Класс postgres бд источника
    """
    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд PostgreSQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return PostgresConnect(**params)


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    is_proxy = False
    query = MysqlQuery()

    def __init__(self, *args, **kwargs):
        super(KmClient, self).__init__(*args, **kwargs)

    @signal()
    def km_signal_1(self):
        pass

    @callback
    def km_callback_1(self, *args, **kwargs):
        pass


class Wsdl(Source):
    """
        Класс источника Wsdl
    """
    type_source = "wsdl"

    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(Wsdl, self).__init__(*args, **kwargs)
