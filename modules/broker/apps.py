# -*- coding: utf-8 -*-

import inspect

from django.apps import AppConfig


class BrokerAppConfig(AppConfig):
    """
        Класс, анализирующий классы и параметры брокера при запуске проекта
    """
    name = 'broker'
    verbose_name = u'Анализ параметров брокера'

    def ready(self):
        # Анализируем источники брокера
        self._analize_sources()

    @classmethod
    def _analize_sources(cls):
        """
            Находит все источники брокера и
            в соответствии с полученным списком обновляет таблицу бд
        """
        from models import SourceModel
        from broker import sources as broker_sources

        # Получаем список имен источников модуля
        module_sources = set(
            name for name, source in inspect.getmembers(broker_sources)
            if hasattr(source, 'is_proxy') and source.is_proxy == False
        )

        # Выбираем источники, которые уже есть в бд
        db_sources = set(
            SourceModel.objects.all().values_list('source', flat=True)
        )

        # Удаляем источники, которых нет в модуле
        SourceModel.objects.filter(source__in=(db_sources - module_sources))\
                           .delete()

        # Добавляем источники, которых нет в бд
        new_sources = module_sources - db_sources
        if new_sources:
            SourceModel.objects.bulk_create(
                [SourceModel(source=name_source) for name_source in new_sources]
            )
