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
        from broker import sources as broker_sources

        # Получаем список имен источников модуля
        module_sources = set(
            name for name, source in inspect.getmembers(broker_sources)
            if getattr(source, 'is_proxy', None) == False
        )

        try:
            # Выбираем источники, которые уже есть в бд
            db_sources = set(
                Source.objects.all().values_list('source', flat=True)
            )

            # Удаляем источники, которых нет в модуле
            Source.objects.filter(source__in=(db_sources - module_sources)) \
                .delete()

            # Добавляем источники, которых нет в бд
            Source.objects.bulk_create([
                Source(source=name_source) for name_source
                in (module_sources - db_sources)
            ])
        except ProgrammingError:
            warnings.warn('Only if deployed')
