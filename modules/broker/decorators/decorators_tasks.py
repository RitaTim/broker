# -*- coding: utf-8 -*-

from functools import wraps

from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from django.utils.module_loading import import_string
from django.conf import settings
from django.db import transaction

from app_celery import app

from logger.models import CallbackLog

task_logger = get_task_logger(__name__)
module_broker = __import__('broker')


def set_state(func, *args, **kwargs):
    """
        Устанавливает состояние таска обработчика
    """
    @wraps(func)
    def wrapper(self, callback_log_id, *args_callback, **kwargs_callback):
        # Выходим, если "обработчик" находится в обработке или уже обработан
        self.callback_log = CallbackLog.objects.get(pk=callback_log_id)
        if self.callback_log.state in CallbackLog.STATES['final']:
            return
        if not self.callback_log.state == 'process':
            with transaction.atomic():
                self.callback_log.state = 'process'
                self.callback_log.save(update_fields=('state',))
        try:
            # в блоке try: ... except: ... нет необходимости исп.
            # refresh_from_db(), так как мы обновляем только
            # состояние/сообщение
            result = func(self, callback_log_id, *args_callback,
                          **kwargs_callback)
            # помечаем таск успешно выполненным
            self.callback_log.refresh_from_db()
            with transaction.atomic():
                self.callback_log.state = 'success'
                self.callback_log.result = result
                self.callback_log.save(update_fields=('state', 'result'))
            # если есть уид таска для отмены, сбрасываем
            self.callback_log.revoke_task(check_task=True,
                                          task_logger=task_logger)
            return result
        except Retry:
            # при повторе мы не меняем атрибуты callback_log
            task_logger.warning(u'Перезапускаем таск')
        except Exception as e:
            # фиксируем ошибку при выполнении таска
            with transaction.atomic():
                self.callback_log.state = 'failure'
                self.callback_log.message = u'{}: {}'.format(type(e), e.message)
                self.callback_log.save(update_fields=('state', 'message'))
                self.callback_log.revoke_task(check_task=True,
                                              task_logger=task_logger)
    return wrapper


def expire_task(func, *args, **kwargs):
    """
        Учитывает следующие параметры таска в kwargs_callback:
            expire - время жизни таска (в сек)
            terminate_in_process - True, если таск нужно завершить

        Через expire сек, после запуска обработчика, завершаем таск, если:
            - состояние обработчика 'pending'
            - состояние обработчика 'process' и terminate_in_process
            установлен в True
        В этом случае установливаем состояние failure
    """
    @wraps(func)
    def wrapper(self, callback_log_id, *args_callback, **kwargs_callback):
        if self.request.retries == 0:
            expire = self.callback_log.params.get('expire', None)
            terminate_in_process = self.callback_log.params.get(
                'terminate_in_process', False)
            if expire:
                # Запускаем таск проверки состояния обработчика через expire
                async_result = check_state_by_expire.apply_async(
                    args=[callback_log_id, terminate_in_process],
                    countdown=expire
                )
                with transaction.atomic():
                    self.callback_log.check_task_uuid = async_result.id
                    self.callback_log.save(update_fields=('check_task_uuid',))
        return func(self, callback_log_id, *args_callback, **kwargs_callback)
    return wrapper


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


def retry_task(func, *args, **kwargs):
    """
        Запускает таск повторно, если таск упал с исключением,
        которое входит в список exсeptions_list_retries (из kwargs) и
        max_retries пока не превышено
    """
    @wraps(func)
    def wrapper(self, callback_log_id, *args_callback, **kwargs_callback):
        max_retries = self.callback_log.params.get('max_retries', 0)
        if not max_retries:
            func(self, callback_log_id, *args_callback, **kwargs_callback)
            return
        # если все же задано максимальное количество повторов
        exceptions_paths_list = self.callback_log.params.get(
            'exceptions_list_retries', [])
        exceptions_list_retries = [
            import_string(exception) for exception in exceptions_paths_list
        ]
        countdown_retries = self.callback_log.params.get(
            'countdown_retries', settings.COUNTDOWN_RETRIES_DEFAULT)
        try:
            return func(self, callback_log_id, *args_callback,
                        **kwargs_callback)
        except tuple(exceptions_list_retries):
            self.retry(countdown=countdown_retries)
    return wrapper
