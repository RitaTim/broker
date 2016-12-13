# -*- coding: utf-8 -*-

from functools import wraps


def signal(*args_signal, **kwargs_signal):
    """
        Декоратор для функции-сигнала
    """
    def decorator(func):
        @wrapped(func, 'is_signal')
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
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

