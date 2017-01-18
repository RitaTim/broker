# -*- coding: utf-8 -*-

from MySQLdb.connections import Connection as MysqlConnection

from broker.sources.database import DataBaseSourse, SqlQuery
from broker.sources.exceptions import MysqlQueryException


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    def __init__(self, *args, **kwargs):
        super(MysqlDBSource, self).__init__(*args, **kwargs)

    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд MySQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return MysqlConnect(**params)


class MysqlConnect(MysqlConnection):
    """
        Коннект к базе mysql
        От Connection доступны методы:
            set_autocommit()
            get_autocommit()
    """
    pass


class MysqlQuery(SqlQuery):
    """
    Объект Query для mysql
    """
    # SQL операции сравнения
    lookups = {
        '': '=',
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
    }
    # SQL шаблоны под каждый тип запроса
    select_template = "broker/sql/mysql/select.html"
    update_template = "broker/sql/mysql/update.html"
    insert_template = "broker/sql/mysql/insert.html"

    def __condition_as_sql(self, conditions):
        """
        Преобразует кортеж условий в строку sql

        кортеж (('field1', 'gt', 10), 'OR', ('field2', 'lt', 20)), 'AND',
               ('field3', '', 0)
        будет преобразован в ((`field1` > 10) OR (`field2` < 20)) AND
                             (field3 = 0)

        :param conditions: tuple условий
        :return: string
        """
        connectors = set(['OR', 'AND'])
        sql = ''
        for condition in conditions:
            if isinstance(condition, (list, tuple)):
                if connectors & set(condition):
                    sql += u' ( {0} ) '\
                           .format(self.__condition_as_sql(condition))
                else:
                    try:
                        sql += u' (`{0}` {1} "{2}") '.format(
                            condition[0],
                            self.lookups[condition[1]],
                            condition[2]
                        )
                    except KeyError:
                        raise MysqlQueryException(
                            u'Операция "{0}" не предусмотрена'.format(
                                condition[1]
                            )
                        )
            elif isinstance(condition, (str, unicode)):
                sql += u' {0} '.format(condition)
        return sql

    def as_select_sql(self, *args, **kwargs):
        """
        Возвращает sql строку типа "SELECT"

        :param table: string имя таблицы
        :param fields: list список полей
        :param where: Q object or dict
            допускается передача в виде объектов Q или словаря, который будет
            преобразован в соответствующий Q(...)
        :param order_by: list список сортировки
            например: ['name', '-price']
        :param limit: list список ограничений
            например: [0, 100]
        :return: string
        """
        params = {
            'conditions': self.__condition_as_sql(
                self.prepare_condition(kwargs.pop('where', None))
            )
        }
        params.update(kwargs)
        return self.as_sql(self.select_template, params)

    def as_update_sql(self, *args, **kwargs):
        """
        Возвращает sql строку типа "UPDATE"

        :param table: string имя таблицы
        :param values: dict обновляемых полей типа:
            {'field1': 'value1', 'field2': 'value2'}
        :param where: Q object or dict
            допускается передача в виде объектов Q или словаря, который будет
            преобразован в соответствующий Q(...)
        """
        params = {
            'conditions': self.__condition_as_sql(
                self.prepare_condition(kwargs.pop('where', None))
            )
        }
        params.update(kwargs)
        return self.as_sql(self.update_template, params)

    def as_insert_sql(self, *args, **kwargs):
        """
        Возвращает sql строку типа "INSERT"

        :param table: string имя таблицы
        :param fields: list список имен полей
        :param value: list список значений полей
        :param values: list список value (при добавлении нескольких строк):
            [['value1', 'value2'], ['value3', 'value4']]
        """
        params = {
            'fields': kwargs.get('fields', []),
            'rows': [kwargs['value']] if kwargs.get('value')
                    else kwargs.get('values', [])
        }
        params.update(kwargs)
        return self.as_sql(self.insert_template, params)
