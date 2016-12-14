# -*- coding: utf-8 -*-

from types import FunctionType


class BaseClassMeta(type):
    """
        Базовый мета-класс
    """
    all_callbacks = []
    all_signals = []

    def __new__(cls, name, bases, attrs):
        new_cls = super(BaseClassMeta, cls).__new__(cls, name, bases, attrs)

        callbacks = []
        signals = []
        for name_attr, attr in attrs.items():
            # проверяем только атрибуты типа функции
            if not isinstance(attr, FunctionType):
                continue

            # расширяем списки коллбэков и сигналов функциями
            # с соответствующими атрибутами
            if hasattr(attr, 'is_callback'):
                callbacks.append(attr)
            if hasattr(attr, 'is_signal'):
                signals.append(attr)

        new_cls.all_callbacks = callbacks
        new_cls.all_signals = signals
        return new_cls

    def get_all_callbacks(cls):
        """
            Возвращает список коллбэков класса
        """
        return cls.all_callbacks

    def get_all_signals(cls):
        """
            Возвращает список сигналов класса
        """
        return cls.all_signals