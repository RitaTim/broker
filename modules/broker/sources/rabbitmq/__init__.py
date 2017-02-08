# -*- coding: utf-8 -*-


"""
Базовым классом источников типа rabbitmq является класс RabbitMQ
Он позволяет вызаимодействовать с внешними приложениями через celery

Для вызова таска во внешнем приложении, необхдодимо вызвать метод
_apply_async и передать ему следующие параметры:
    useless_task: string - имя таска
    ignore_result: bool - True, если нужно игнорировать результат тасков
    additional_params: dict - дополнительные параметры из Правила
    task_args: list|tuple - args, переданные в сигнал
    task_kwargs: dict # kwargs, переданные в сигнал

Пример реализации источника TestRabbitMQ:
    class TestRabbitMQ(RabbitMQ):
        @signal()
        def send_signal(self, *args, **kwargs):
            pass

        @callback()
        def callback(self, *args, **kwargs):
            # Вызываем таск useless_task во внешнем приложении,
            # не возвращая результат
            return self._apply_async(
                'useless_task',
                ignore_result=True,
                additional_params=kwargs.pop('additional_params', None),
                task_args=args,
                task_kwargs=kwargs
            )

При этом у источника TestRabbitMQ в init_params должны быть указаны параметры {
    "main": "magic", # имя приложения
    "broker": "amqp://angel:angel@localhost:5672/magic", # BROKER_URL приложения
    "backend": "amqp" # backend, для хранения результата (если не нужно
                      # сохранять результат тасков, можно не указывать)
}
"""



from copy import deepcopy

from celery import Celery, signature
from broker.sources import Source


class RabbitMQ(Source):
    """
        Класс источника RabbitMQ

        В init_params источников данного типа необходимо указывать параметры:
        {
            'app_name': <имя приложения>
            'broker_url': <BROKER_URL проекта>
        }
    """
    type_source = "rabbitmq"
    celery_settings = {
        "queue": "default",
        "serializer": "json"
    }

    def __init__(self, *args, **kwargs):
        super(RabbitMQ, self).__init__(*args, **kwargs)
        self.init_params = self.source_model.init_params
        self.app = Celery(**self.init_params)

    def get_default_celery_settings(self, custom_celery_settings=None):
        """
            Возвращает конфигурацию для app.Celery
            :param custom_celery_settings: дополнительные параметры
        """
        result = deepcopy(self.celery_settings)
        if custom_celery_settings:
            result.update(custom_celery_settings)
        return result

    def _apply_async(self, task_signature, ignore_result=False,
                     additional_params=None, task_args=None, task_kwargs=None):
        """
        Вызывает таск на стороне RabbitMQ источника
        :param task_signature: string сигнатура вызова таска
        :param ignore_result: bool признак "игнорировать результат от внешнего
        приложения"
        :param additional_params: dict дополнительные параметры (можно задать
        queue, routing_key, ...)
        :param task_args: list неименованные параметры
        :param task_kwargs: dict именованные параметры
        :return: результат выполнения таска
        """
        signature_task = signature(task_signature, app=self.app)
        async_result = signature_task.apply_async(
            args=task_args or (),
            kwargs=task_kwargs or {},
            **self.get_default_celery_settings(additional_params)
        )
        if not ignore_result:
            # мы ожидаем окончание выполнение таска и возвращаем его результат
            # для дальнейшего логирования
            external_task_result = async_result.get()
            if async_result.state == 'FAILURE':
                # при возникновении ошибки на стороне внешнего приложения,
                # async_result.state == 'FAILURE', а в async_result.traceback
                # содержится ее traceback
                raise Exception(async_result.traceback)
            return external_task_result
        # не возвращаем результат выполнения внешнего таска, если явно
        # игнорируем результат
        return
