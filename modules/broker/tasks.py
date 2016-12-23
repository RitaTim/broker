# -*- coding: utf-8 -*-

import json

from app_celery.analize import app

from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(name="send_signal")
def send_signal(*args, **kwargs):
    from .forms import SignalLogForm

    # Подготавливаем данные для формы логирования
    # Преобразуем необходимые параметры в json
    for attr_name in ['params', 'args_signal', 'kwargs_signal']:
        kwargs[attr_name] = json.dumps(kwargs.get(attr_name, {}))

    log_form = SignalLogForm(data=kwargs)
    if log_form.is_valid():
        log_form.save()
        return
    logger.error(u"Error creating SignalLog object. "
                 u"Form log_form is not valid. {}".format(log_form.errors))

