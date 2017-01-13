# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache

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

    def get_init_params(self):
        """
           Возвращает параметры источника из кэша или из базы
        """
        try:
            connections_sources = cache.get('CONNECTIONS_SOURCES')
            return connections_sources[self.source]
        except KeyError:
            return self.init_params

    @property
    def db_alias(self):
        """
            Возвращает alias базы данных источника
        """
        return get_db_allias_for_source(self.source)


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
        # Обновляем закэшированные настройки бд
        connections_sources = cache.get('CONNECTIONS_SOURCES', {})
        connections_sources[instance.db_alias] = instance.init_params
        cache.set('CONNECTIONS_SOURCES', connections_sources)


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
