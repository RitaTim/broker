# -*- coding: utf-8 -*-

from django.contrib.postgres.fields import JSONField
from django.db import models

from broker.models import Source

from app_celery import app


class SignalLogAbstract(models.Model):
    """
        Абстрактная модель для логирования событий. Включает в себя поля:
            source - источник
            signature - наименование сигнала
            args_signal - args, с которыми вызывался метод сигнала
            kwargs_signal - kwargs, с которыми вызывался метод сигнала
            params - параметры вызова таска
            created - дата создания
    """
    source = models.ForeignKey(Source, verbose_name=u"Источник",
                               related_name="%(app_label)s_%(class)s_source")
    signature = models.CharField(u"Сигнатура", max_length=128)
    args_signal = JSONField(null=True, blank=True)
    kwargs_signal = JSONField(null=True, blank=True)
    params = JSONField(null=True, blank=True)

    class Meta:
        abstract = True


class SignalLog(SignalLogAbstract):
    """
        Модель для хранения недавних логов событий
    """
    created = models.DateTimeField(u"Дата создания", auto_now_add=True)


class SignalLogHistory(SignalLogAbstract):
    """
        Модель для хранения архива логов событий
        Добавили поля id и created, чтобы при создании эти значения можно было
        задавать не автоматически. Берем эти значения из SignalLog
    """
    id = models.IntegerField(primary_key=True)
    created = models.DateTimeField(u"Дата создания")


class CallbackLogAbstract(models.Model):
    """
        Модель для логирования данных по обработчикам событий.
        Включает в себя поля:
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
            callback_args - args обработчика из декоратора @callback
            callback_kwargs - kwargs обработчика из декоратора @callback
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

    destination = models.ForeignKey(
        Source, verbose_name=u"Приемник",
        related_name="%(app_label)s_%(class)s_destination"
    )
    callback = models.CharField(u"Обработчик", max_length=128)
    params = JSONField(null=True, blank=True)
    state = models.CharField(u"Состояние", max_length=128,
                             choices=STATE_CHOICES, default='pending')
    message = models.TextField(u"Сообщение", null=True, blank=True)
    result = JSONField(null=True, blank=True)
    callback_args = JSONField(null=True, blank=True)
    callback_kwargs = JSONField(null=True, blank=True)
    task_uuid = models.UUIDField(u"Uuid таска", null=True, blank=True)
    check_task_uuid = models.UUIDField(u"Uuid таска отмены", null=True,
                                       blank=True)
    updated = models.DateTimeField(u"Дата обновления", auto_now=True)

    def revoke_task(self, check_task=False, task_logger=None):
        """
            Убивает основной таск обработчика, если НЕ check_task,
            иначе останавливает таск, проверяющий на expire
        """
        task_uuid = self.check_task_uuid if check_task else self.task_uuid
        if task_uuid:
            app.control.revoke(str(task_uuid), terminate=True,
                               signal='SIGKILL')
            if task_logger:
                task_logger.info(u'Сбрасываем task "{0}" по отмене'
                                 .format(task_uuid))

    class Meta:
        abstract = True


class CallbackLog(CallbackLogAbstract):
    """
        Модель для хранения недавних логов обработчиков
        Включает все поля абстрактной модели и signal_logger - лог сигнала
    """
    signal_logger = models.ForeignKey(SignalLog,
                                      verbose_name=u"Лог события",
                                      related_name="signal_logger")
    created = models.DateTimeField(u"Дата создания", auto_now_add=True)


class CallbackLogHistory(CallbackLogAbstract):
    """
        Модель для хранения архива логов обработчиков
        Включает все поля абстрактной модели и signal_logger - лог сигнала
    """
    signal_logger = models.ForeignKey(SignalLogHistory,
                                      verbose_name=u"Лог события",
                                      related_name="signal_logger")
    created = models.DateTimeField(u"Дата создания")