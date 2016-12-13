# -*- coding: utf-8 -*-

from decorators import signal, callback
from types import FunctionType


class BaseClass(type):
    """
        Базовый класс для классов всех типов источников
    """
    all_callbacks = []
    all_signals = []

    def __new__(cls, name, bases, attrs):
        new_cls = super(BaseClass, cls).__new__(cls, name, bases, attrs)

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


class DataBaseSourse(object):
    """
        Класс, описывающий тип источника "База данных"
    """
    __metaclass__ = BaseClass

    @signal(2, 20, 'data_base_sourse')
    def f1(self):
        print "f1"

    @signal()
    def f2(self):
        print "f2"

    @callback
    def f3(self):
        print "f3"

    def f4(self):
        print "f4"


class FileSourse(object):
    """
        Класс, описывающий тип источника "Файл"
    """
    __metaclass__ = BaseClass

    @signal()
    def f2_(self):
        print "f2"

    @callback
    def f3_(self):
        print "f3"

    def f4_(self):
        print "f4"
