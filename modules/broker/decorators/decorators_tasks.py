# -*- coding: utf-8 -*-

from functools import wraps

from celery.utils.log import get_task_logger

from django.utils.module_loading import import_string
from django.conf import settings

from app_celery.analize import app

from logger.models import CallbackLog

logger = get_task_logger(__name__)
module_broker = __import__('broker')


def set_state_callback(func, *args, **kwargs):
    """
        Устанавливает состояние таска обработчика
    """
    @wraps(func)
    def wrapper(self, callback_log_id, *args_callback, **kwargs_callback):
        # Если установлено одно из финальных состояний, то выходим, иначе
        final_states = ['success', 'failure']
        callbacks_logs = CallbackLog.objects.filter(id=callback_log_id)
        if callbacks_logs.filter(state__in=final_states).exists():
            return

        callbacks_logs.update(state='process')

        try:
            result = func(self, callback_log_id, *args_callback,
                          **kwargs_callback)
            # Если состояние обработчика во время выполнения не изменилось,
            # то считаем, что он успешно выполнен
            CallbackLog.objects.filter(id=callback_log_id, state='process')\
                               .update(state='success', message='')
            return result
        except Exception as e:
            # Логируем ошибку и состояние failure
            CallbackLog.objects.filter(id=callback_log_id)\
                               .exclude(state__in=final_states)\
                               .update(state='failure', message=e.message)
    return wrapper


def retry_task(func, *args, **kwargs):
    """
        Запускает таск повторно, если таск упал с исключением,
        которое входит в список exeptions_list_retries (из kwargs) и
        max_retries пока не превышено
    """
    @wraps(func)
    def wrapper(self, callback_log_id, *args_callback, **kwargs_callback):
        exceptions_paths_list = kwargs_callback.get(
            'exceptions_list_retries', []
        )
        exceptions_list_retries = [
            import_string(exp_path) for exp_path in exceptions_paths_list
        ]
        countdown_retries = kwargs_callback.get('countdown_retries',
                                                settings.COUNTDOWN_DEFAULT)
        if not countdown_retries:
            func(self, callback_log_id, *args_callback, **kwargs_callback)
            return

        try:
            func(self, callback_log_id, *args_callback, **kwargs_callback)
        except tuple(exceptions_list_retries):
            self.retry(countdown=countdown_retries, throw=False,
                       **kwargs_callback)

    return wrapper


def expire_task(func, *args, **kwargs):
    """
        Учитывает следующие параметры таска в kwargs_callback:
            expire - время жизни таска
            terminate_process - True, если таск нужно завершить

        Через expire времени после запуска обработчика и проверяет:
            если таск не завершился И (terminate_process == True):
            завершает таск принудительно и установливает состояние failure
    """
    @wraps(func)
    def wrapper(self, callback_log_id, *args_callback, **kwargs_callback):
        expire = kwargs_callback.pop('expire', None)
        terminate_in_process = kwargs_callback.pop('terminate_in_process', None)

        if expire and not getattr(self, 'check_expire', None):
            # Запускаем таск проверки состояния обработчика через expire
            check_state_by_expire.apply_async(
                args=[callback_log_id, terminate_in_process],
                countdown=expire
            )
            self.check_expire = True
        return func(self, callback_log_id, *kwargs_callback, **kwargs_callback)
    return wrapper


@app.task(name="check_state_by_expire", queue="callbacks")
def check_state_by_expire(callback_log_id, terminate_in_process, *args, **kwargs):
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
    callbacks_logs = CallbackLog.objects.filter(id=callback_log_id)
    callback_log = callbacks_logs.first()
    state = callback_log.state
    if state == 'process' and not terminate_in_process:
        callbacks_logs.update(message='Skip expired')
    if state == 'pending' or (state == 'process' and terminate_in_process):
        callbacks_logs.update(state='failure',
                              message='Task stopped by expire')
        app.control.revoke(callback_log.uuid_task.hex)
