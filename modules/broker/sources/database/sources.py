# -*- coding: utf-8 -*-

from django.utils import timezone

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

    @callback()
    @transaction_atomic
    def response_report_equipment_repair(self, *args, **kwargs):
        """
            Выпоняет действия, необходимые после получения отчета:
            обновляет данные buffer
        """
        where = {'id': kwargs.get('id')}

        msg_out = self.get_message_out(
            self.tempate_msg_out,
            {
                "code_answer": kwargs.get('status'),
                "msg_answer": kwargs.get('message')
            }
        )
        updated_fields = {
            'state': 'F' if kwargs.get('status') == '0' else 'E',
            'time_out': timezone.now().strftime("%Y%m%d%I%M%S"),
            'message_out': msg_out,
            'data': kwargs.get('data')
        }
        self.update_buffer(where, **updated_fields)
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

    def get_message_out(self, template, context_data):
        """
            Возвращает данные  по шаблону
            :param template_name: имя шаблона
            :param context: контекст
        """
        return Template(template).render(Context(context_data))
