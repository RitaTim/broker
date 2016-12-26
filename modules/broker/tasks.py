# -*- coding: utf-8 -*-

import json
from celery.utils.log import get_task_logger

from django.forms import ValidationError

from app_celery.analize import app
from logger.forms import SignalLogForm, CallbackLogForm

from .models import Rule


logger = get_task_logger(__name__)


@app.task(name="send_signal")
def send_signal(*args, **kwargs):
    """
        Осуществляет логирование сигналов и обработчиков,
        а также анализ правил и запуск коллбэков
    """
    # Подготавливаем данные для формы логирования
    # Преобразуем необходимые параметры в json
    for attr_name in ['params', 'args_signal', 'kwargs_signal']:
        kwargs[attr_name] = json.dumps(kwargs.get(attr_name, {}))

    # Логируем поступление сигнала
    signal_log_form = SignalLogForm(data=kwargs)
    if not signal_log_form.is_valid():
        raise ValidationError(
            u"Error creating SignalLog object. "
            u"Form signal_log_form is not valid. {}"
            .format(signal_log_form.errors)
        )
    signal_log_form.save()

    # Анализ правил
    cleaned_data = signal_log_form.cleaned_data
    rules = Rule.objects.filter(
        source=cleaned_data.get('source'),
        signal=cleaned_data.get('signature')
    )

    signal_logger_pk = signal_log_form.instance.pk
    for rule in rules:
        # логируем callback
        callback_log_form = CallbackLogForm(data={
            'signal_logger': signal_logger_pk,
            'destination': rule.destination.pk,
            'callback': rule.callback,
            'state': 'pending'
        })
        if not callback_log_form.is_valid():
            raise ValidationError(
                u"Error creating CallbackLogobject. "
                u"Form callback_log_form is not valid. {}"
                .format(callback_log_form.errors)
            )
        callback_log_form.save()

        # Запускаем callback
        void_callback.apply_async(kwargs={
            'callback_log': callback_log_form.instance
        })


@app.task(name="void_callback")
def void_callback(*args, **kwargs):
    callback_log = kwargs.get('callback_log')
    callback_log.state = 'process'
    callback_log.save()
