# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings

from app_celery import app
from django.db import transaction

from .models import CallbackLog, CallbackLogHistory, SignalLog,\
    SignalLogHistory


@app.task(name="clear_logs", queue="control")
@transaction.atomic
def clear_logs():
    """
        Очистка логов
    """
    now = datetime.now()
    move_time = now - timedelta(days=settings.KEEP_BROKER_LOGS)
    death_time = now - timedelta(days=settings.KEEP_BROKER_LOGS_HISTORY)

    # Получаем логи сигналов, которые нужно перенести в историю
    old_signal_logs = SignalLog.objects.filter(created__lte=move_time)
    # Копируем логи сигналов в таблицу с историей
    SignalLogHistory.objects.bulk_create([
        SignalLogHistory(**log_values)
        for log_values in old_signal_logs.values()
    ])

    # Получаем список логов обработчиков по списку логов сигналов
    old_callback_logs = CallbackLog.objects.filter(
        signal_logger_id__in=old_signal_logs.values_list('id', flat=True)
    )
    # Копируем логи обработчиков в таблицу с историей
    CallbackLogHistory.objects.bulk_create([
        CallbackLogHistory(**log_values)
        for log_values in old_callback_logs.values()
    ])

    # Удаляем из таблицы перемещенные логи сигналов
    old_signal_logs.delete()
    # Удаляем устаревшие логи из истории
    SignalLogHistory.objects.filter(created__lte=death_time).delete()
