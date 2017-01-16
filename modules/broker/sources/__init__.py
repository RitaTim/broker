# -*- coding: utf-8 -*-


class TransactionAtomicManager(object):
    """
        Отключает autocommit на время выполнения функции и
        откатывает изменения в случае ошибки
    """
    def __init__(self, connector, *args, **kwargs):
        super(TransactionAtomicManager, self).__init__()
        self.connector = connector
        self.autocommit = self.connector.get_autocommit()

    def __enter__(self, *args, **kwargs):
        if self.autocommit:
            self.connector.set_autocommit(False)

    def __exit__(self, exc_type, exc_value, traceback):
        if not exc_type:
            self.connector.commit()
        else:
            # В случае ошибки, откатываем изменения
            self.connector.rollback()

        if self.autocommit:
            self.connector.set_autocommit(True)
