# -*- coding: utf-8 -*-

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
    def update_user_status(self, *args, **kwargs):
        """
            Вызвать таск на блокировку домена
        """
        self.apply_async(
            'update_users_status',
            ignore_result=True,
            additional_params=kwargs.pop('additional_params', None),
            task_args=args,
            task_kwargs=kwargs
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
