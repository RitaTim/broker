# -*- coding: utf-8 -*-

from broker.decorators.decorators import signal, callback
from broker.sources.database.mysql import MysqlDBSource


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    @signal()
    def request_report_equipment_repair(self):
        """
            Запросить отчет о ремонте оборудования
        """
        pass

    @callback
    def update_buffer(self, *args, **kwargs):
        """
            Обновляет таблицу буфера
            В kwargs должны быть:
                task_id - id обновляемой строки
                и значения полей, которые нужно обновить
        """
        self.update(
            table='buffer',
            where={'id': kwargs.pop('task_id', None)},
            values=kwargs
        )
        return {'Values were set ': kwargs}
