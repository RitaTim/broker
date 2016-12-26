# -*- coding: utf-8 -*-

import json

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
    args_signal = JSONField(default=json.dumps([]), null=True, blank=True)
    kwargs_signal = JSONField(default=json.dumps({}), null=True, blank=True)
    params = JSONField(default=json.dumps({}), null=True, blank=True)
    date_create = models.DateTimeField(u"Дата создания", auto_now_add=True)


class CallbackLog(models.Model):
    """
        Модель для логирования данных по обработчикам событий
    """
    STATE_CHOICES = (
        ('pending', 'Pending'),
        ('process', 'Process'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    )

    STATE_DEFAULT = 'pending'

    signal_logger = models.ForeignKey(SignalLog, verbose_name=u"Лог события",
                                      related_name="signal_logger")
    destination = models.CharField(u"Приемник", max_length=128)
    callback = models.CharField(u"Callback", max_length=128)
    params = JSONField(default=json.dumps({}), null=True, blank=True)
    state = models.CharField(u"Состояние", max_length=128,
                             choices=STATE_CHOICES, default=STATE_DEFAULT)
    message = models.TextField(u"Сообщение", null=True, blank=True)
    result = JSONField(default=json.dumps({}), null=True, blank=True)
