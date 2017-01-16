# -*- coding: utf-8 -*-

"""
    Данная реализация позволяет представить все необходимые Source'ы (источники
    и получатели) в виде моделей в базе данных.

    Естественно, что при запуске initial миграций (deploy проекта), данный код
    будет генерировать SQL ошибки.
"""


import inspect
import warnings

from django.apps import AppConfig
from django.db.utils import ProgrammingError
from django.conf import settings
from django.core.cache import cache

from .helpers import get_db_allias_for_source


class BrokerAppConfig(AppConfig):
    """
        Класс, анализирующий классы и параметры брокера при запуске проекта
    """
    name = 'broker'
    verbose_name = u'Анализ параметров брокера'

    def ready(self):
        """
            Находит все источники брокера и
            в соответствии с полученным списком обновляет таблицу бд
        """
        from models import Source
        from broker.sources import sources as broker_sources

        # Получаем список имен источников модуля и их типы
        module_sources = {
            name: source.type_source for name, source in
            inspect.getmembers(broker_sources)
            if getattr(source, 'is_proxy', None) == False
        }
        module_sources_names = set(module_sources.keys())

        try:
            # Выбираем источники, которые уже есть в бд
            db_sources_names = set(
                Source.objects.all().values_list('source', flat=True)
            )

            # Удаляем источники, которых нет в модуле
            Source.objects.filter(
                source__in=(db_sources_names - module_sources_names )
            ).delete()

            # Добавляем источники, которых нет в бд
            Source.objects.bulk_create([
                Source(
                    source=source_name,
                    type_source=module_sources[source_name]
                ) for source_name in (module_sources_names - db_sources_names)
            ])

            # Определяем список коннекторов к источникам - бд
            db_sources_data = {
                get_db_allias_for_source(source): params
                for source, params in Source.objects.filter(type_source='db')
                                            .values_list('source',
                                                         'init_params')
            }
            # Кэшируем параметры источников БД
            cache.set(
                 settings.CONNECTIONS_SOURCES_KEY, db_sources_data,
                 settings.DB_SOURCES_CACHE_TIME
            )
        except ProgrammingError:
            warnings.warn('Only if deployed')
