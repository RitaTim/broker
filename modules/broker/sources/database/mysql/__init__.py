# -*- coding: utf-8 -*-

from MySQLdb.connections import Connection as MysqlConnection

from django.template import Template, Context

from broker.sources.database import DataBaseSourse, SqlQuery
from broker.sources.exceptions import MysqlQueryException


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
        'in': 'IN'
    }
    # Шаблоны для lookups'ов
    condition_templates = {
        'in': '({% for val in value %}"{{ val }}"{% if not forloop.last %}, {% endif %}{% endfor %})'
    }

    # SQL шаблоны под каждый тип запроса
    select_template = "sql/mysql/select.html"
    update_template = "sql/mysql/update.html"
    insert_template = "sql/mysql/insert.html"

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
        connectors = ('OR', 'AND')
        sql = ''
        for condition in conditions:
            if isinstance(condition, (list, tuple)):
                if any([(connector in condition) for connector in connectors]):
                    sql += u' ( {0} ) '.format(
                        self.__condition_as_sql(condition)
                    )
                else:
                    try:
                        tmpl_code = self.condition_templates.get(
                            condition[1], '"{{ value }}"')
                        sql += u' (`{0}` {1} {2}) '.format(
                            condition[0],
                            self.lookups[condition[1]],
                            Template(tmpl_code)
                                .render(Context({'value': condition[2]}))
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
        :param for_update: использовать FOR UPDATE (по умолчанию False)
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


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    query = MysqlQuery()

    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд MySQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return MysqlConnect(**params)

    def get_cursor(self):
        return self.connector.cursor()


class MysqlConnect(MysqlConnection):
    """
        Коннект к базе mysql
        От Connection доступен метод get_autocommit()
    """
    def set_autocommit(self, value):
        """
        Устанавливаем значение autocommit
        :param value: bool
        """
        self.autocommit(value)
