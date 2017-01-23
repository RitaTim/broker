# -*- coding: utf-8 -*-

from datetime import datetime

from broker.sources.wsdl import Wsdl
from broker.decorators.decorators import callback, signal


class OneSWsdl(Wsdl):
    """
        Доступ к wsdl серверу
    """
    @signal()
    def received_report_equipment_repair(self):
        """
            Получен отчет о ремонте оборудования
        """
        pass

    @signal()
    def change_task_state_buffer(self):
        """
            Изменилось состояние таска в buffer
        """
        pass

    @callback
    def get_report_equipment_repair(self, *args, **kwargs):
        """
            Возвращает отчет о статусе ремонта оборудования
            В kwargs должны быть следующие параметры:
            {
                'id': <id записи>
                'uuid': <uuid отчета>,
                'begindate': <дата создания>,
                'enddate': <дата получения>,
                'email': <e-mail>
            }
        """
        date_f = "%Y%m%d"
        result = dict(self.wsdl_client.service.ReportEquipmentRepairStatus2(
            kwargs['id'], kwargs['user_uuid'],
            datetime.strptime(kwargs['begindate'], date_f),
            datetime.strptime(kwargs['enddate'], date_f), kwargs['mail']
        ))
        # Кидаем сигнал о том, что отчет получен

        self.received_report_equipment_repair(
            id=kwargs['id'], data=result.get('return'), state='F',
            time_out=datetime.now().strftime("%Y%m%d%I%M%S")
        )
        return result
