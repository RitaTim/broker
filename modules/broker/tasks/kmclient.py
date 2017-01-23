# -*- coding: utf-8 -*-

import re

from app_celery import app
from celery.utils.log import get_task_logger

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


@app.task(name="analyze_buffer_kmclient", bind=True)
def analyze_buffer_kmclient(self, *args, **kwargs):
    """
        Анализирует таблицу buffer, выбирая все таски, у которых:
            opcode = 10 (получение отчетов по ремонту)
            state = N (новые)
        И вызывает сигнал на получение отчета для каждого полученного таска
    """
    km = KmClient()
    # Устанавливаем состояние в P - process
    new_tasks = km.select(table='buffer',  where={'state': 'N', 'opcode': 10},
                          for_update=True)
    for new_task in new_tasks:
        km.update_buffer(new_task['id'], state='P')
        message_in = get_params_from_string(
            new_task['message_in'],
            params=['begindate', 'enddate', 'mail', 'agreement']
        )
        new_task.update(message_in)
        km.request_report_equipment_repair(**new_task)