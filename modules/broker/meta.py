# -*- coding: utf-8 -*-

from types import FunctionType


class BaseClassMeta(type):
    """
        Базовый мета-класс
    """

    __callback_params = dict()
    __all_callbacks = []
    __all_signals = []

    def __new__(cls, name, bases, attrs):
        new_cls = super(BaseClassMeta, cls).__new__(cls, name, bases, attrs)

        callback_params = dict()
        signals = []

        # Добавляем сигналы и обработчики родителей
        parent_callbacks = []
        parent_signals = []
        for base_cls in bases:
            if hasattr(base_cls, 'get_all_callbacks'):
                parent_callbacks = base_cls.get_all_callbacks()
            if hasattr(base_cls, 'get_all_signals'):
                parent_signals = base_cls.get_all_signals()

        for name_attr, attr in attrs.items():
            # проверяем только атрибуты типа функции
            if not isinstance(attr, FunctionType):
                continue

            # расширяем списки коллбэков и сигналов функциями
            # с соответствующими атрибутами
            if hasattr(attr, 'is_callback'):
                callback_params[name_attr] = {
                    'args': getattr(attr, 'callback_args', None),
                    'kwargs': getattr(attr, 'callback_kwargs', None)
                }

                func_error = callback_params[name_attr].get('kwargs', {})\
                                                       .get('func_error')
                if func_error:
                    # Если указан неполный путь, полагаем,
                    # что функция находится в текущем модуле
                    if not "." in func_error:
                        callback_params[name_attr]["kwargs"]["func_error"] = \
                            ".".join([new_cls.__module__, func_error])

            if hasattr(attr, 'is_signal'):
                signals.append(name_attr)

        new_cls.__callback_params = callback_params
        new_cls.__all_callbacks = parent_callbacks + callback_params.keys()
        new_cls.__all_signals = parent_signals + signals
        return new_cls

    def get_all_callbacks(cls):
        """
            Возвращает список коллбэков класса
        """
        return cls.__all_callbacks

    def get_all_signals(cls):
        """
            Возвращает список сигналов класса
        """
        return cls.__all_signals

    def get_callback_params(cls, callback_name=None):
        """
        Возвращает параметры декоратора callback'а

        :param callback_name: string название метода
        :return:
        """
        return cls.__callback_params.get(callback_name, {})
