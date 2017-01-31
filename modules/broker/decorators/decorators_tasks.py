# -*- coding: utf-8 -*-

from functools import wraps

from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from django.utils.module_loading import import_string
from django.conf import settings
from django.db import transaction

from logger.models import CallbackLog

task_logger = get_task_logger(__name__)


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

            # Если указана функция для вызова при ошибке, вызываем ее
            func_error = self.callback_log.callback_kwargs.get('func_error')
            if func_error:
                callback_error = import_string(func_error)
                if callable(callback_error):
                    callback_error(
                        type(e), e, *self.request.args, **self.request.kwargs
                    )

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
                from broker.tasks import check_state_by_expire
                async_result = check_state_by_expire.apply_async(
                    args=[callback_log_id, terminate_in_process],
                    countdown=expire
                )
                with transaction.atomic():
                    self.callback_log.check_task_uuid = async_result.id
                    self.callback_log.save(update_fields=('check_task_uuid',))
        return func(self, callback_log_id, *args_callback, **kwargs_callback)
    return wrapper


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
            return func(self, callback_log_id, *args_callback,
                        **kwargs_callback)
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
