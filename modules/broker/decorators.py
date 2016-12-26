# -*- coding: utf-8 -*-

from functools import wraps

from .tasks import send_signal


def signal(*args, **kwargs):
    """
        Декоратор для функции-сигнала
    """
    def decorator(func):
        @wrapped(func, 'is_signal')
        def wrapper(self, *args_method, **kwargs_method):
            # Формируем параметры сигнала
            send_signal.apply_async(kwargs={
                'source': self.source_model.pk,
                'signature': func.func_name,
                'args_signal': args_method,
                'kwargs_signal': kwargs_method,
                'params': kwargs    # для логирования
            }, **kwargs)
        return wrapper
    return decorator


def callback(func):
    """
        Декоратор для функции-коллбэка
    """
    @wrapped(func, 'is_callback')
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    return wrapper


def wrapped(func, attr_name, attr_val=True):
    """
        Устанавливает значение конкретного атрибута функции
            func - функция
            attr_name - имя атрибута
            attr_val - значение атрибута
        И возвращает стандартную обертку для функции
    """
    setattr(func, attr_name, attr_val)
    return wraps(func)

