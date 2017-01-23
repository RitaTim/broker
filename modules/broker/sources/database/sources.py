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
    def response_report_equipment_repair(self, *args, **kwargs):
        """
            Выпоняет действия, необходимые после получения отчета:
            обновляет данные buffer
        """
        pk = kwargs.pop('id', None)
        self.update_buffer(pk, **kwargs)
        return 'Task {} was successfully updated'.format(pk)

    def update_buffer(self, id, **kwargs):
        """
            Обновляет строку таблицы буфера
            В kwargs должны быть:
                id - id обновляемой строки
                и значения полей, которые нужно обновить
        """
        self.update(
            table='buffer',
            where={'id': id},
            values=kwargs
        )
