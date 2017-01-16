# -*- coding: utf-8 -*-

from MySQLdb.connections import Connection
from psycopg2 import connect as postgres_connect


class MysqlConnect(Connection):
    """
        Коннект к базе mysql
        От Connection доступны методы:
            set_autocommit()
            get_autocommit()
    """
    def get_cursor(self):
        """
            Возварщает указатель бд
        """
        return self.cursor()


class PostgresConnect(object):
    """
        Коннект к базе postgres
    """
    connector = None

    def __init__(self, **kwargs):
        super(PostgresConnect, self).__init__()
        self.connector = postgres_connect(**kwargs)

    def set_autocommit(self, value):
        """
            Включает/выключает режим autocommit в зависимости от value
        """
        self.connector.autocommit = value

    def get_autocommit(self):
        """
            Возвращает текущее значение autocommit
        """
        return self.connector.autocommit

    def get_cursor(self):
        """
            Возварщает указатель бд
        """
        return self.connector.cursor()