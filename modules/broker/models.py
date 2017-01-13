# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.db.backends.mysql.base import DatabaseWrapper
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField

from .helpers import get_db_allias_for_source


class Source(models.Model):
    """
        Модель для хранения информации об источниках
    """
    source = models.CharField(u"Источника", max_length=128)
    type_source = models.CharField(u"Тип источника", max_length=128,
                                   null=True, blank=True)
    init_params = JSONField(null=True, blank=True)

    def __unicode__(self):
        return self.source


@receiver(pre_save, sender=Source)
def pre_save_source(sender, instance, **kwargs):
    """
        Обновляет коннектор бд источника,
        в случае если изменились его параметры
    """
    try:
        old_instance = Source.objects.get(pk=instance.pk)
    except Source.DoesNotExist:
        # При добавлении элемента ничего не делаем
        return

    if old_instance.init_params != instance.init_params:
        # Обновляем текущий коннектор
        db_alias = get_db_allias_for_source(instance.source)
        settings.CONNECTIONS_SOURCES[db_alias] = DatabaseWrapper(
            instance.init_params
        )


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
    params = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ("source", "destination", "signal", "callback")
