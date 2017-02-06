# -*- coding: utf-8 -*-

from celery import signature

from broker.sources.rabbitmq import RabbitMQ
from broker.decorators.decorators import callback, signal


class MailerRabbitMQ(RabbitMQ):
    """
        Источник для взаимодействия с проектом mailer через RabbitMq
    """
    @signal()
    def post_save_emaildomain(self):
        """
            Сохранился emaildomain
        """
        pass

    @signal()
    def pre_delete_emaildomain(self):
        """
            emaildomain будет удален
        """
        pass

    @signal()
    def update_emails(self):
        """
            Обновились emails
        """
        pass

    @callback()
    def update_user_status(self, additional_params=None, **kwargs):
        """
            Вызвать таск на блокировку домена
        """
        signature_task = signature('update_users_status', app=self.app)
        signature_task.apply_async(
            kwargs=kwargs,
            **self.get_default_celery_settings(additional_params)
        )


class MailerSNRRabbitMQ(MailerRabbitMQ):
    """
        Источник для взаимодействия с проектом mailer-snr через RabbitMq
    """
    pass


class MailerMebelRabbitMQ(MailerRabbitMQ):
    """
        Источник для взаимодействия с проектом mailer-mebel через RabbitMq
    """
    pass
