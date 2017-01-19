# -*- coding: utf-8 -*-

from broker.decorators.decorators import signal, callback
from broker.sources.database import DataBaseSourse
from broker.sources.database.mysql import MysqlDBSource, MysqlQuery
from broker.sources.database.postgres import PostgresConnect


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    @signal()
    def km_signal_1(self):
        pass

    @callback
    def km_callback_1(self, *args, **kwargs):
        pass
