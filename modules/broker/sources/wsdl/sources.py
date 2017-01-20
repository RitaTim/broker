# -*- coding: utf-8 -*-

from broker.sources.wsdl import Wsdl
from broker.decorators.decorators import callback


class OneSWsdl(Wsdl):
    """
        Доступ к wsdl серверу
    """

    @callback
    def get_report_equipment_repair_status(self, *args, **kwargs):
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
        result = self.wsdl_client.service.ReportEquipmentRepairStatus2(
            kwargs['task_id'], kwargs['uuid'], kwargs['start_date'],
            kwargs['end_date'], kwargs['email']
        )
        result['return'] = result['return'].decode('hex')
        return dict(result)
