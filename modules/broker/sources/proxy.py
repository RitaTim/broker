# -*- coding: utf-8 -*-

from broker.decorators.decorators_helpers import transaction_atomic
from broker.meta import BaseClassMeta
from broker.models import Source as SourceModel
from broker.sources.sql import SqlQuery
from broker.sources.exceptions import DBConnectError


class BaseClass(object):
    """
        Базовый класс
    """
    __metaclass__ = BaseClassMeta

    # По умолчанию, класс является промежуточным звеном между инстансом и
    # базовым классом. В классе реального источника, нужно установить False
    is_proxy = True


class Source(BaseClass):
    """
        Базовый класс для всех источников
    """
    type_source = None
    source_model = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__()
        cls_name = self.__class__.__name__
        try:
            self.source_model = SourceModel.objects.get(source=cls_name)
        except SourceModel.DoesNotExist:
            raise ValueError("Source '{}' not has object of model"
                             .format(cls_name))


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    type_source = "db"
    connector = None
    cursor = None
    query = SqlQuery()

    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД
        try:
            # Инициализируем connector для работы с бд
            self.connector = self.get_connector(
                self.source_model.get_init_params()
            )
        except Exception as e:
            raise DBConnectError(e.message)

    def get_connector(self, params={}):
        """
        Возвращает connector к бд
        :return: Connection
        """
        raise NotImplemented

    def select(self, *args, **kwargs):
        """
            Выполняет "select" запрос

            В **kwargs передаем:
                table - имя таблицы
                fields - список полей
                where - условия выборки
                order_by - условия сортировки
                limit - условия ограничения
        """
        cursor = self.connector.get_cursor()
        cursor.execute(
            self.query.as_select_sql(*args, **kwargs)
        )
        return cursor.fetchall()

    @transaction_atomic
    def update(self, *args, **kwargs):
        """
            Выполняет "update" запрос

            В **kwargs передаем:
                table - имя таблицы
                value - устанавливаемые значения
                where - условия выборки
        """
        self.connector.get_cursor().execute(
            self.query.as_update_sql(*args, **kwargs)
        )

    @transaction_atomic
    def insert(self, *args, **kwargs):
        """
            Выполняет "insert" запрос

            В **kwargs передаем:
                table - имя таблицы
                value - сохраняемые значения
        """
        self.connector.get_cursor().execute(
            self.query.as_insert_sql(*args, **kwargs)
        )

    def delete(self, *args, **kwargs):
        """
            Выполняет "delete" запрос

            В **kwargs передаем:
                table - имя таблицы
                where - условия выборки
        """
        return self.connector.get_cursor().execute(
            self.query.as_delete_sql(*args, **kwargs)
        )
