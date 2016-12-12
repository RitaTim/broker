# -*- coding: utf-8 -*-

from functools import wraps


def signal(max_retries=1, expire=60, routing_key='default'):
    """
        Декоратор для функции-сигнала
    """
    def decorator(func):
        func.is_signal = True

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
        return wrapper
    return decorator


def callback(func):
    """
        Декоратор для функции-коллбэка
    """
    func.is_callback = True

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    return wrapper
