# -*- coding: utf-8 -*-

from broker.decorators.decorators import signal, callback
from broker.sources.database import DataBaseSourse
from broker.sources.database.mysql import MysqlDBSource, MysqlQuery
from broker.sources.database.postgres import PostgresConnect


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


class PostgresSQL(DataBaseSourse):
    """
        Класс postgres бд источника
    """
    is_proxy = False

    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд PostgreSQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return PostgresConnect(**params)
