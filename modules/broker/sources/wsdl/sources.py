# -*- coding: utf-8 -*-

import uuid
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
            Метод ReportEquipmentRepairStatus() требует следующие параметры:
             'id' - id записи,
             'user_uuid' - uuid дилера. Ожидает тип UUID
             'agreement' - uuid соглашения. Ожидает тип UUID
             'begindate' - начало формирования отчета. Ожидает тип datetime
             'enddate' - конец формирования отчета. Ожидает тип datetime
             'mail' - e-mail
        """
        date_f = "%Y%m%d"
        wsdl_return = dict(self.wsdl_client.service.ReportEquipmentRepairStatus(
            kwargs['id'], uuid.UUID(kwargs['user_uuid']),
            uuid.UUID(kwargs['agreement']),
            datetime.strptime(kwargs['begindate'], date_f),
            datetime.strptime(kwargs['enddate'], date_f), kwargs['mail']
        )).get('return')
        # Кидаем сигнал о том, что отчет получен
        self.received_report_equipment_repair(
            id=kwargs['id'], data=getattr(wsdl_return, 'Data', ''),
            message=unicode(getattr(wsdl_return, '_Message', '')),
            status=str(getattr(wsdl_return, '_Status', 0))
        )
        return wsdl_return
