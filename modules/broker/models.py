# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.postgres.fields import JSONField

from .helpers import get_db_allias_for_source


class Source(models.Model):
    """
        Модель для хранения информации об источниках
    """
    source = models.CharField(u"Источника", max_length=128)
    type_source = models.CharField(u"Тип источника", max_length=128,
                                   null=True, blank=True)
    init_params = JSONField(u"Параметры источника", null=True, blank=True)

    def __unicode__(self):
        return self.source

    @property
    def db_alias(self):
        """
            Возвращает alias базы данных источника
        """
        return get_db_allias_for_source(self.source)


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
    callback = models.CharField(u"Обработчик", max_length=128, blank=True)
    params = JSONField(u"Параметры вызова обработчика", null=True, blank=True)
    additional_params = JSONField(u"Дополнительные параметры", null=True,
                                  blank=True)

    class Meta:
        unique_together = ("source", "destination", "signal", "callback")
