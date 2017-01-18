# -*- coding: utf-8 -*-

"""
    Для определения коннектора необходимо создать объект одного из классов,
    у которого есть миксин PostgresConnectMixin и
    который унаследован от broker.sources.connection

    Формирование данных для connection реализовано на основе метода connect
    в psycopg2

    Инициализация была вынесена в миксин для корректного вызова конструктора
    класса родителя

    Пример использования:
        from broker.sources import connections
        PC = connections.PostgresConnect
        NPC = connections.NamedTuplePostgresConnect
        p = PC(**{
            'dbname': 'test',
            'user': 'us',
            'password': 'ps',
            'host': '127.0.0.1'
        })
        cur = p.cursor()

    Примечание!
        p.cursor() вернет корректный ответ только если async=False

"""

from psycopg2 import _param_escape
from psycopg2._psycopg import connection as PostgresConnection
from psycopg2.extras import NamedTupleConnection


class PostgresConnectMixin(object):
    """
        Миксин для источников бд postgres
        Формирует данные для connection и вызывает конструктор
    """
    def __init__(self, dsn=None, **kwargs):
        cursor_factory = kwargs.pop('cursor_factory', None)
        async = kwargs.pop('async', False)

        if not dsn:
            ordered_list = ('dbname', 'user', 'password', 'host', 'port')
            items = []
            for field in ordered_list:
                value = kwargs.pop(field, None)
                if value:
                    items.append((field, value))

            items.extend(
                [(k, v) for (k, v) in kwargs.iteritems() if v is not None])

        if dsn is not None and items:
            raise TypeError(
                "'%s' is an invalid keyword argument when the dsn is specified"
                % items[0][0])

        if dsn is None:
            if not items:
                raise TypeError('missing dsn and no parameters')
            else:
                dsn = " ".join(["%s=%s" % (k, _param_escape(str(v)))
                                for (k, v) in items])

        super(PostgresConnectMixin, self).__init__(dsn, async)

        if cursor_factory:
            self.cursor_factory = cursor_factory

    def set_autocommit(self, value):
        """
            Включает/выключает режим autocommit в зависимости от value
        """
        self.autocommit = value

    def get_autocommit(self):
        """
            Возвращает текущее значение autocommit
        """
        return self.autocommit


class PostgresConnect(PostgresConnectMixin, PostgresConnection):
    """
        Коннект к базе postgress
    """
    pass


class NamedTuplePostgresConnect(PostgresConnectMixin, NamedTupleConnection):
    """
        Тестовый класс коннектора
    """
    pass
