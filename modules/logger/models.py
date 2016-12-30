# -*- coding: utf-8 -*-

from django.contrib.postgres.fields import JSONField
from django.db import models

from broker.models import Source


class SignalLog(models.Model):
    """
        Модель для логирования событий. Включает в себя поля:
            source - источник
            signature - наименование сигнала
            args_signal - args, с которыми вызывался метод сигнала
            kwargs_signal - kwargs, с которыми вызывался метод сигнала
            params - параметры вызова таска
            date_create - дата создания
    """
    source = models.ForeignKey(Source, verbose_name=u"Источник",
                               related_name="signal_log_source")
    signature = models.CharField(u"Сигнатура", max_length=128)
    args_signal = JSONField(null=True, blank=True)
    kwargs_signal = JSONField(null=True, blank=True)
    params = JSONField(null=True, blank=True)
    date_create = models.DateTimeField(u"Дата создания", auto_now_add=True)


class CallbackLog(models.Model):
    """
        Модель для логирования данных по обработчикам событий.
        Включает в себя поля:
            signal_logger - лог сигнала
            destination - приемник сигнала
            callback - название обработчика сигнала
            params - параметры, с которыми будет вызываться callback
            state - состояние таска обработчика:
                pending - в ожидании
                process - выполняется
                success - успешно завершен
                failure - завершен с ошибкой
            message - сообщение
            result - результат таска
            created - дата создания
            updated - дата обновления
    """
    STATE_CHOICES = (
        ('pending', u'В ожидании'),
        ('process', u'Выполняется'),
        ('success', u'Успешно завершён'),
        ('failure', u'Завершен с ошибкой'),
    )

    STATES = {
        'start': ('pending',),
        'process': ('process',),
        'final': ('success', 'failure')
    }

    signal_logger = models.ForeignKey(SignalLog, verbose_name=u"Лог события",
                                      related_name="signal_logger")
    destination = models.ForeignKey(Source, verbose_name=u"Приемник",
                                    related_name="callback_log_source")
    callback = models.CharField(u"Обработчик", max_length=128)
    params = JSONField(null=True, blank=True)
    state = models.CharField(u"Состояние", max_length=128,
                             choices=STATE_CHOICES, default='pending')
    message = models.TextField(u"Сообщение", null=True, blank=True)
    result = JSONField(null=True, blank=True)
    task_uuid = models.UUIDField(u"Uuid таска", null=True, blank=True)
    created = models.DateTimeField(u"Дата создания", auto_now_add=True)
    updated = models.DateTimeField(u"Дата обновления", auto_now=True)
