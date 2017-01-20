# -*- coding: utf-8 -*-

"""
    Для определения коннектора необходимо создать объект одного из классов, у
    которого есть миксин PostgresConnectMixin

    Формирование данных для connection реализовано на основе метода connect
    в psycopg2

    Инициализация была вынесена в миксин для корректного вызова конструктора
    класса родителя

    Пример использования:
        from broker.sources.database.postgres import PostgresConnect

        p = PostgresConnect(**{
            'dbname': 'test',
            'user': 'us',
            'password': 'ps',
            'host': '127.0.0.1'
        })
        cur = p.cursor()

    Примечание!
        p.cursor() вернет корректный ответ только если async=False

    В случае, если нужно использовать нестандартный connection,
    выполните следующие действия:
        - импортируйте необходимый connection
        - создайте класс-наследник

    Пример с NamedTupleConnection:

    from psycopg2.extras import NamedTupleConnection

    class NamedTuplePostgresConnect(PostgresConnectMixin, NamedTupleConnection):
        pass

"""

from psycopg2 import _param_escape
from psycopg2._psycopg import connection as PostgresConnection

from broker.sources.database import DataBaseSourse, SqlQuery


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
        self.autocommit = bool(value)

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


class PostgresqlQuery(SqlQuery):
    """
        Объект Query для postgres
    """
    # TODO: добавить функционал работы с sql для postgres (аналогия MysqlQuery)
    pass


class PostgresSQL(DataBaseSourse):
    """
        Класс postgres бд источника
    """

    query = PostgresqlQuery()

    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд PostgreSQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return PostgresConnect(**params)
