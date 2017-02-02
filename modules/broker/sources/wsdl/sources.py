# -*- coding: utf-8 -*-

import uuid
from suds import WebFault
from datetime import datetime

from broker.sources.wsdl import Wsdl
from broker.decorators.decorators import callback, signal
from broker.sources.exceptions import WsdlAnswerException


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

    @callback(func_error='set_error_state')
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
        try:
            date_f = "%Y%m%d"
            wsdl_return = dict(
                self.wsdl_client.service.ReportEquipmentRepairStatus(
                    kwargs['id'], uuid.UUID(kwargs['user_uuid']),
                    uuid.UUID(kwargs['agreement']),
                    datetime.strptime(kwargs['begindate'], date_f),
                    datetime.strptime(kwargs['enddate'], date_f),
                    kwargs['mail']
                )
            ).get('return')
            # Кидаем сигнал о том, что отчет получен
            wsdl_message = unicode(getattr(wsdl_return, '_Message', ''))
            self.received_report_equipment_repair(
                id=kwargs['id'],
                status=str(getattr(wsdl_return, '_Status', 0)),
                data=getattr(wsdl_return, 'Data', ''),
                message=wsdl_message
            )
            return wsdl_message
        except WebFault as error:
            # Реагируем только на exceptions, по которым нужно перезапускать
            # и генерируем WsdlAnswerException для них
            raise WsdlAnswerException(error.message)


def set_error_state(exc_type, exc, *args, **kwargs):
    """
        Устанавливает состояние записи в buffer с ошибкой
    """
    one_s_wsdl = OneSWsdl()
    one_s_wsdl.received_report_equipment_repair(
        id=kwargs['id'], status='8', data='',
        message=u"Время ожидания результата истекло"
    )
