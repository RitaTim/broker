# -*- coding: utf-8 -*-

import json
from copy import deepcopy

from celery.utils.log import get_task_logger
from django.core.mail import mail_admins

from app_celery.analize import app
from logger.models import CallbackLog
from logger.forms import SignalLogForm, CallbackLogForm
from logger.exceptions import LogFormValidateError


logger = get_task_logger(__name__)
module_broker = __import__('broker')


@app.task(name="send_signal")
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
            u'Signal "{0}" from source "{1}" was generated not correct'.format(
                data['signature'], data['source']),
            signal_log_form.errors
        )
    signal_log = signal_log_form.save()

    # Анализ правил
    rules = signal_log_form.get_rules()
    for rule in rules:
        # логируем callback
        params = deepcopy(signal_log_form.cleaned_data['params'])
        params.update(rule.params or {})
        callback_log_form = CallbackLogForm({
            'signal_logger': signal_log.pk,
            'destination': rule.destination.pk,
            'callback': rule.callback,
            'params': json.dumps(params)
        })
        try:
            if not callback_log_form.is_valid():
                raise LogFormValidateError(
                    u'Callback "{0}" from source "{1}" generated not correct'
                    .format(rule.callback, rule.destination.source),
                    callback_log_form.errors
                )

            callback_log = callback_log_form.save()

            # Запускаем callback
            receive_signal.apply_async(
                args=[callback_log.pk] + signal_log.args_signal,
                kwargs=signal_log.kwargs_signal,
                **params
            )
        except LogFormValidateError as e:
            err_msg = u"{}: {}".format(e.message, e.errors)
            logger.error(err_msg)
            mail_admins(u"Ошибка при вызове callbacks", u"",
                        html_message=err_msg)


@app.task(name="receive_signal")
def receive_signal(callback_log_id, *args, **kwargs):
    """
        Запуск обработчика сигнала
    """
    callback_log = CallbackLog.objects.get(id=callback_log_id)
    destination_intance = getattr(module_broker.sources,
                                  callback_log.destination.source)()
    callback = getattr(destination_intance, callback_log.callback)
    if callable(callback):
        callback(*args, **kwargs)
