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
                'task_id': <id отчета>
                'uuid': <uuid отчета>,
                'start_date': <дата создания>,
                'end_date': <дата получения>,
                'email': <e-mail>
            }
        """
        # Устанавливаем состояние в P - process
        self.change_task_state_buffer(task_id=kwargs['task_id'], state='P')

        date_f = "%Y%m%d"
        result = dict(self.wsdl_client.service.ReportEquipmentRepairStatus2(
            kwargs['task_id'], kwargs['uuid'],
            datetime.strptime(kwargs['start_date'], date_f),
            datetime.strptime(kwargs['end_date'], date_f), kwargs['email']
        ))
        # Кидаем сигнал о том, что отчет получен

        self.received_report_equipment_repair(
            task_id=kwargs['task_id'], data=result.get('return'), state='F',
            time_out=datetime.now().strftime("%Y%m%d%I%M%S")
        )
        return result
