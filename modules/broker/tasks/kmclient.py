# -*- coding: utf-8 -*-

import re

from app_celery import app
from celery.utils.log import get_task_logger

from broker.sources import TransactionAtomicManager
from broker.sources.database.sources import KmClient


task_logger = get_task_logger(__name__)


__all__ = [
    'analyze_buffer_kmclient',
]


def get_params_from_string(line, params=[]):
    """
        Возвращает словарь параметров params из строки line
    """
    return dict(
        [
            (name_field, value) for name_field, value
            in re.findall('(\w+)=\"(.+?)\"', line)
            if not params or name_field in params
        ]
    )


@app.task(name="analyze_buffer_kmclient")
def analyze_buffer_kmclient(*args, **kwargs):
    """
        Анализирует таблицу buffer, выбирая все таски, у которых:
            opcode = 10 (получение отчетов по ремонту)
            state = N (новые)
        Формирует для каждого выбранного таска набор параметров типа: {
            'id': 202,
            'user_uuid': u"a0e2c270-b1f8-11e2-93f1-002655df3ac1",
            'agreement': u"eff368fc-b3c2-11e2-93f1-002655df3ac1",
            'begindate': "20130101",
            'enddate': "20130102",
            'mail': ''
        } и вызывает сигнал на получение отчета для каждого полученного таска
        с этими параметрами
    """
    km = KmClient()
    with TransactionAtomicManager(km.connector):
        new_tasks = km.select(
            table='buffer',
            where={'state': 'N', 'opcode': 10},
            for_update=True
        )
        ids = []
        for new_task in new_tasks:
            params_in_message = get_params_from_string(
                new_task['message_in'],
                params=['begindate', 'enddate', 'mail', 'agreement']
            )
            params_in_message.update({
                'id': new_task['id'],
                'user_uuid': new_task['user_uuid']
            })
            km.request_report_equipment_repair(**params_in_message)
            # собираем список анализируемых id-ников
            ids.append(params_in_message['id'])
        if ids:
            # Устанавливаем состояние P ("В работе")
            km.update_buffer({'id__in': ids}, state='P')
