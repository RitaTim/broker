# -*- coding: utf-8 -*-

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

        result = dict(self.wsdl_client.service.ReportEquipmentRepairStatus2(
            kwargs['task_id'], kwargs['uuid'], kwargs['start_date'],
            kwargs['end_date'], kwargs['email']
        ))
        # Кидаем сигнал о том, что отчет получен

        time_out = 20161120100813 # todo: haha
        self.received_report_equipment_repair(
            task_id=kwargs['task_id'], data=result.get('return'), state='F',
            time_out=time_out
        )
        return result
