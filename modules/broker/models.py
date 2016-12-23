# -*- coding: utf-8 -*-

import json

from django.db import models
from django.contrib.postgres.fields import JSONField


class Source(models.Model):
    """
        Модель для хранения информации об источниках
    """
    source = models.CharField(u"Тип источника", max_length=128)
    init_params = JSONField(default=json.dumps({}), null=True, blank=True)

    def __unicode__(self):
        return self.source


class Rule(models.Model):
    """
        Модель для хранения правил. Одно правило - связка сигнала источника
        с коллбэком приемника
    """
    source = models.ForeignKey(Source, verbose_name=u"Источник",
                               related_name="rules_source")
    destination = models.ForeignKey(Source, verbose_name=u"Приемник",
                                    related_name="rules_destination")
    signal = models.CharField(u"Сигнал", max_length=128, blank=True)
    callback = models.CharField(u"Callback", max_length=128, blank=True)

    class Meta:
        unique_together = ("source", "destination", "signal", "callback")


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
