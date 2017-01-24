# -*- coding: utf-8 -*-

from datetime import datetime

from broker.decorators.decorators import signal, callback
from broker.decorators.decorators_helpers import transaction_atomic
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
    @transaction_atomic
    def response_report_equipment_repair(self, *args, **kwargs):
        """
            Выпоняет действия, необходимые после получения отчета:
            обновляет данные buffer
        """
        where = {'id': kwargs.pop('id', None)}
        kwargs.update({
            'state': 'F',
            'time_out': datetime.now().strftime("%Y%m%d%I%M%S")
        })
        self.update_buffer(where, **kwargs)
        return u'Строки с условием {0} успешно обновлены'.format(where)

    def update_buffer(self, where, **kwargs):
        """
            Обновляет строку таблицы буфера
            В kwargs должны быть:
                id - id обновляемой строки
                и значения полей, которые нужно обновить
        """
        self.update(
            table='buffer',
            where=where,
            values=kwargs
        )
