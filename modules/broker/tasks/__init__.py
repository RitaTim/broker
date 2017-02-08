# -*- coding: utf-8 -*-

import json
from copy import deepcopy

from app_celery import app
from broker.decorators.decorators_tasks import set_state, retry_task, \
    expire_task
from broker.helpers import get_cls_module
from broker.models import Source
from celery.utils.log import get_task_logger
from django.core.mail import mail_admins
from django.db import transaction
from django.shortcuts import get_object_or_404
from logger.exceptions import LogFormValidateError
from logger.forms import SignalLogForm, CallbackLogForm
from logger.models import CallbackLog

from .kmclient import analyze_buffer_kmclient

task_logger = get_task_logger(__name__)


@app.task(name="send_signal", queue="logger")
def send_signal(*args, **kwargs):
    """
        Осуществляет логирование сигналов и обработчиков,
        а также анализ правил и запуск коллбэков
    """
    # Подготавливаем данные для формы логирования
    json_value = ('params', 'args_signal', 'kwargs_signal')
    data = dict(
        [(key, json.dumps(value) if key in json_value else value)
         for key, value in kwargs.iteritems()]
    )
    # Логируем поступление сигнала
    signal_log_form = SignalLogForm(data)
    if not signal_log_form.is_valid():
        raise LogFormValidateError(
            u'Сигнал "{0}" от источника "{1}" сгенерирован с ошибкой'.format(
                data['signature'], data['source']),
            signal_log_form.errors
        )

    with transaction.atomic():
        signal_log = signal_log_form.save()
    # Анализ правил
    rules = signal_log_form.get_rules()
    for rule in rules:
        # логируем callback

        # Параметры вызова обработчика береуться из params сигнала,
        # обновленных параметрами правила
        params = deepcopy(signal_log.params)
        params.update(rule.params or {})

        destination_cls = get_cls_module(rule.destination.source)
        callback_params = destination_cls.get_callback_params(rule.callback)
        callback_log_form = CallbackLogForm({
            'signal_logger': signal_log.pk,
            'destination': rule.destination.pk,
            'callback': rule.callback,
            'callback_args': json.dumps(callback_params.get('args', ())),
            'callback_kwargs': json.dumps(callback_params.get('kwargs', {})),
            'params': json.dumps(params),
            'additional_params': json.dumps(rule.additional_params)
        })
        # и вызываем его
        if callback_log_form.is_valid():
            callback_log = callback_log_form.save()
            # Запускаем callback
            async_result = receive_signal.apply_async(
                args=[callback_log.pk] + signal_log.args_signal,
                kwargs=signal_log.kwargs_signal,
                **params
            )
            callback_log.task_uuid = async_result.id
            with transaction.atomic():
                callback_log.save()
        else:
            err_msg = u"Обработчик '{0}' для '{1}' задан не корректно: {2}"\
                .format(rule.callback, rule.destination.source,
                        callback_log_form.errors)
            task_logger.error(err_msg)
            mail_admins(u"Ошибка при анализе правила", u"",
                        html_message=err_msg)


@app.task(name="receive_signal", bind=True, queue="receiver")
@set_state
@expire_task
@retry_task
def receive_signal(self, callback_log_id, *args, **kwargs):
    """
        Запуск обработчика сигнала
    """
    callback_log = CallbackLog.objects.get(id=callback_log_id)
    name_source = callback_log.destination.source
    destination_instance = get_cls_module(name_source)()
    callback = getattr(destination_instance, callback_log.callback)
    if callable(callback):
        # вспомогательные параметры из правила "additional_params" передаем в
        # kwargs'ах; их обязательно надо извлечь из kwargs'ов, перед передачей
        # внешнему таску (см. реализацию метода apply_task)
        if callback_log.additional_params:
            kwargs['additional_params'] = callback_log.additional_params
        return callback(*args, **kwargs)
    task_logger.warning(u'Обработчик "{0}" не является методом'.format(
        callback_log.callback))


@app.task(name="check_state_by_expire", queue="control")
def check_state_by_expire(callback_log_id, terminate_in_process):
    """
        Проверяет состояние обработчика по истечении expire
        Если обработчик еще выполняется И terminate_in_process=False:
            - добавляем сообщение в лог, о том,что expire проигнорирован
        Если (обработчик выполняется И terminate_in_process=True) ИЛИ
        обработчик не запущен:
            - меняем состояние на failure
            - добавляем соответствующее сообщение в лог
            - останавливаем таск
    """
    callback_log = CallbackLog.objects.get(pk=callback_log_id)
    if (callback_log.state in CallbackLog.STATES['process']
            and not terminate_in_process):
        task_logger.warning(u'Не могу сбросить (не задан параметр '
                            u'"terminate_in_process")')
    elif callback_log.state in CallbackLog.STATES['start'] \
            or (callback_log.state in CallbackLog.STATES['process']
                and terminate_in_process):
        callback_log.revoke_task(task_logger=task_logger)
        with transaction.atomic():
            callback_log.state = 'failure'
            callback_log.message = 'Skipped by "check_state_by_expire"'
            callback_log.save(update_fields=('state', 'message'))


@app.task(name="send_signal_to_broker", queue="rabbit")
def send_signal_to_broker(source, signature, args_signal=None,
                          kwargs_signal=None, params=None, **kwargs):
    """
        Отлавливает сообщения из очереди rabbit и вызывает
        соответствующие сигналы, если есть. Ожидает параметры:
            'source': 'KmClient', # имя источника
            'signal': 'request_reipment_repair', # сигнал
            'args_signal': (), # args, с кот будет вызываться сигнал
            'kwargs_signal': {}, # kwargs, с кот будет вызываться сигнал
            'params': {}, # параметры обработчика
    """
    source = get_object_or_404(Source, source=source)
    cls = get_cls_module(source.source)
    # Проверка на существование сигнала
    if signature not in cls.get_all_signals():
        raise BrokerSendSignalError(
            u"Source {} does not has signal {}"
            .format(source.source, signature)
        )

    send_signal.apply_async(kwargs={
        # источник сигнала
        'source': source.id,
        # его сигнатура
        'signature': signature,
        # неименованные параметры сигнала
        'args_signal': args_signal,
        # именованные параметры сигнала
        'kwargs_signal': kwargs_signal,
        # параметры для обработчика
        'params': params,
    })


class BrokerSendSignalError(Exception):
    """
        Генерируется, когда возникает ошибка при генерации нужного сигнала
    """
    pass
