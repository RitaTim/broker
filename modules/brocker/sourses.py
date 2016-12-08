# -*- coding: utf-8 -*-

from decorators import is_signal, is_callback
from types import FunctionType


class BaseClass(type):
    """
        Базовый класс для классов всех типов источников
    """
    all_callbacks = []
    all_signals = []

    def __new__(cls, name, bases, attrs):
        new_cls = super(BaseClass, cls).__new__(cls, name, bases, attrs)
        all_functions = [
            (x, y) for x, y in attrs.items() if isinstance(y, FunctionType)
        ]

        cls.set_all_callbacks(new_cls, all_functions)
        cls.set_all_signals(new_cls, all_functions)
        return new_cls

    @classmethod
    def set_all_callbacks(cls, child_cls, all_functions):
        """
            Устанавливает список коллбэков класса
        """
        child_cls.all_callbacks = cls.get_functions_by_decorator_name(
            'callback', all_functions
        )

    @classmethod
    def set_all_signals(cls, child_cls, all_functions):
        """
            Устанавливает список сигналов класса
        """
        child_cls.all_signals = cls.get_functions_by_decorator_name(
            'signal', all_functions
        )

    @classmethod
    def get_functions_by_decorator_name(cls, func_name, all_functions):
        """
            Возвращает список функций класса по имени декоратора
        """
        result = []

        def get_decorators(func):
            """
                Возвращает список декораторов функции
            """
            result = []
            if func.func_closure:
                for func_closure in func.func_closure:
                    if isinstance(func_closure.cell_contents, FunctionType):
                        result.append(func)
                        result.extend(
                            get_decorators(func_closure.cell_contents)
                        )
            return result

        for f_name, func in all_functions:
            if func.func_closure:
                decorators_names = [f.func_name for f in get_decorators(func)]
                if func_name in decorators_names:
                    result.append(func)
        return result

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

    @is_callback
    @is_signal(2, 20, 'data_base_sourse')
    def f1(self):
        print "f1"

    @is_signal()
    def f2(self):
        print "f2"

    @is_callback
    def f3(self):
        print "f3"

    def f4(self):
        print "f4"


class FileSourse(object):
    """
        Класс, описывающий тип источника "Файл"
    """
    __metaclass__ = BaseClass

    @is_signal()
    def f2_(self):
        print "f2"

    @is_callback
    def f3_(self):
        print "f3"

    def f4_(self):
        print "f4"
