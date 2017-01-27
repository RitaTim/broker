# -*- coding: utf-8 -*-

from datetime import datetime

from django.template import Template, Context

from broker.decorators.decorators import signal, callback
from broker.decorators.decorators_helpers import transaction_atomic
from broker.sources.database.mysql import MysqlDBSource


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    tempate_msg_out = u"<?xml version='1.0'?\>" \
                      u"<answer code='{{code_answer}}' msg='{{msg_answer}}'/>"

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
        msg_out = self.get_message_out(
            self.tempate_msg_out,
            {
                "code_answer": kwargs.pop('status'),
                "msg_answer": kwargs.pop('message')
            }
        )
        kwargs.update({
            'state': 'F',
            'time_out': datetime.now().strftime("%Y%m%d%I%M%S"),
            'message_out': msg_out
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

    def get_message_out(self, template_name, context_data):
        """
            Возвращает данные  по шаблону
            :param template_name: имя шаблона
            :param context: контекст
        """
        return Template(template_name).render(Context(context_data))
